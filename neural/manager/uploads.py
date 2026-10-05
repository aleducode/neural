"""Chunked video upload.

Three steps: `init` opens the session and reports which chunks are already
there, `chunk` receives one, `complete` joins them into the Video. Resumable
because `init` on the same file returns what already arrived instead of
starting over.

The client proposes the chunk size but it is clamped here: a huge chunk
defeats the point of splitting the file, and a tiny one makes thousands of
requests.
"""

import secrets
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.utils import timezone
from django.views import View

from neural.manager.views import SuperStaffRequiredMixin
from neural.services import cloudflare_stream
from neural.training.models import Video, VideoUpload

MIN_CHUNK = 256 * 1024          # 256 KB
MAX_CHUNK = 16 * 1024 * 1024    # 16 MB
MAX_SIZE = 4 * 1024 * 1024 * 1024  # 4 GB


class VideoUploadView(SuperStaffRequiredMixin, View):
    """One endpoint, three actions. All behind the panel session."""

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        if action == "direct":
            return self._direct(request)
        if action == "init":
            return self._init(request)
        if action == "chunk":
            return self._chunk(request)
        if action == "complete":
            return self._complete(request)
        if action == "confirm":
            return self._confirm(request)
        return JsonResponse({"error": "Acción desconocida."}, status=400)

    def _direct(self, request):
        """Ask Cloudflare for a one-time upload URL.

        With no token configured it answers `fallback`, and the client uses the chunked
        upload against our own storage. Saying so explicitly keeps the browser from
        having to guess from a 500."""
        if not cloudflare_stream.is_configured():
            return JsonResponse(
                {
                    "mode": "fallback",
                    "reason": "Cloudflare Stream no está configurado (falta CLOUDFLARE_STREAM_TOKEN).",
                }
            )

        filename = (request.POST.get("filename") or "").strip()
        try:
            size = int(request.POST.get("size", 0))
        except (TypeError, ValueError):
            size = 0
        if not filename or size <= 0:
            return JsonResponse({"error": "Falta el archivo."}, status=400)
        if size > MAX_SIZE:
            return JsonResponse(
                {"error": f"El archivo supera el máximo de {MAX_SIZE // (1024**3)} GB."},
                status=400,
            )

        try:
            upload_url, uid = cloudflare_stream.create_direct_upload(filename, size)
        except Exception as error:  # requests o Cloudflare
            return JsonResponse({"error": str(error)}, status=502)

        # The Video row is created right away, as a draft: if the upload breaks,
        # the record still points at the right uid and can be resumed.
        video = Video.objects.create(
            name=filename.rsplit(".", 1)[0],
            source=Video.Source.STREAM,
            stream_uid=uid or "",
        )
        VideoUpload.objects.create(
            token=secrets.token_urlsafe(24),
            filename=filename,
            size=size,
            chunk_size=MIN_CHUNK,
            direct_url=upload_url or "",
            stream_uid=uid or "",
            video=video,
        )
        return JsonResponse(
            {"mode": "stream", "uploadUrl": upload_url, "uid": uid, "videoId": video.pk}
        )

    def _init(self, request):
        try:
            size = int(request.POST.get("size", 0))
            chunk_size = int(request.POST.get("chunkSize", 0))
        except (TypeError, ValueError):
            return JsonResponse({"error": "Tamaños inválidos."}, status=400)

        filename = (request.POST.get("filename") or "").strip()
        if not filename or size <= 0:
            return JsonResponse({"error": "Falta el archivo."}, status=400)
        if size > MAX_SIZE:
            return JsonResponse(
                {"error": f"El archivo supera el máximo de {MAX_SIZE // (1024**3)} GB."},
                status=400,
            )
        chunk_size = max(MIN_CHUNK, min(chunk_size or MIN_CHUNK, MAX_CHUNK))

        # Resuming: the same fingerprint (name + size + chunk) still open is the
        # same upload. That way a page refresh does not re-send 2 GB.
        upload = VideoUpload.objects.filter(
            filename=filename,
            size=size,
            chunk_size=chunk_size,
            completed_at__isnull=True,
        ).first()
        if not upload:
            upload = VideoUpload.objects.create(
                token=secrets.token_urlsafe(24),
                filename=filename,
                size=size,
                chunk_size=chunk_size,
            )

        return JsonResponse(
            {
                "token": upload.token,
                "chunkSize": upload.chunk_size,
                "totalChunks": upload.total_chunks,
                "received": sorted(set(upload.received)),
            }
        )

    def _chunk(self, request):
        upload = self._get(request)
        if upload is None:
            return JsonResponse({"error": "Subida no encontrada."}, status=404)

        try:
            index = int(request.POST.get("index"))
        except (TypeError, ValueError):
            return JsonResponse({"error": "Índice inválido."}, status=400)
        if not 0 <= index < upload.total_chunks:
            return JsonResponse({"error": "Índice fuera de rango."}, status=400)

        part = request.FILES.get("chunk")
        if not part:
            return JsonResponse({"error": "Falta el trozo."}, status=400)

        path = upload.chunk_path(index)
        if default_storage.exists(path):
            default_storage.delete(path)
        default_storage.save(path, part)

        if index not in upload.received:
            upload.received = sorted(set(upload.received) | {index})
            upload.save(update_fields=["received", "modified"])

        return JsonResponse(
            {"received": len(set(upload.received)), "total": upload.total_chunks}
        )

    def _complete(self, request):
        upload = self._get(request)
        if upload is None:
            return JsonResponse({"error": "Subida no encontrada."}, status=404)
        if not upload.is_complete:
            missing = sorted(set(range(upload.total_chunks)) - set(upload.received))
            return JsonResponse(
                {"error": "Faltan trozos.", "missing": missing}, status=409
            )

        # Joined in order and deleted: keeping the chunks would double the storage
        # used by every video, forever.
        target = Video(name=upload.filename.rsplit(".", 1)[0], source=Video.Source.UPLOAD)
        target.save()
        target.file.save(upload.filename, ContentFile(b""), save=True)

        with default_storage.open(target.file.name, "wb") as out:
            for index in range(upload.total_chunks):
                path = upload.chunk_path(index)
                with default_storage.open(path, "rb") as part:
                    for block in iter(lambda p=part: p.read(1024 * 1024), b""):
                        out.write(block)
                default_storage.delete(path)

        # default_storage.delete removes files, not folders: on local disk an
        # empty directory was left behind by every upload.
        folder = Path(default_storage.path(f"uploads/{upload.token}")) if hasattr(default_storage, "path") else None
        if folder and folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()

        upload.video = target
        upload.completed_at = timezone.now()
        upload.save(update_fields=["video", "completed_at", "modified"])

        return JsonResponse(
            {"videoId": target.pk, "name": target.name, "url": target.playback}
        )

    def _confirm(self, request):
        """After the browser finished with Cloudflare: fetch the duration and mark the
        video as ready."""
        video = Video.objects.filter(
            stream_uid=request.POST.get("uid", ""), source=Video.Source.STREAM
        ).first()
        if not video:
            return JsonResponse({"error": "Video no encontrado."}, status=404)

        data = cloudflare_stream.get_video(video.stream_uid) or {}
        duration = data.get("duration") or 0
        video.duration_seconds = int(duration) if duration and duration > 0 else 0
        video.stream_ready = bool((data.get("status") or {}).get("state") == "ready")
        video.save(update_fields=["duration_seconds", "stream_ready", "modified"])

        VideoUpload.objects.filter(stream_uid=video.stream_uid).update(
            completed_at=timezone.now()
        )
        return JsonResponse(
            {
                "videoId": video.pk,
                "name": video.name,
                "ready": video.stream_ready,
                "duration": video.duration_seconds,
                "poster": video.poster,
            }
        )

    @staticmethod
    def _get(request):
        return VideoUpload.objects.filter(
            token=request.POST.get("token", ""), completed_at__isnull=True
        ).first()
