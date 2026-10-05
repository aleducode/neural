"""Refresh videos that Cloudflare was still encoding.

A direct upload returns as soon as the bytes land, but Cloudflare keeps
encoding afterwards: duration and the ready flag are not known yet. The panel
asks once right after the upload and can miss it, so this catches up.

Meant for a periodic job. Only touches rows that are not ready, so it stays
cheap no matter how big the library grows.
"""

from django.core.management.base import BaseCommand

from neural.services import cloudflare_stream
from neural.training.models import Video


class Command(BaseCommand):
    help = "Syncs duration and ready state for videos still encoding on Stream."

    def handle(self, *args, **options):
        if not cloudflare_stream.is_configured():
            self.stderr.write(self.style.ERROR("CLOUDFLARE_STREAM_TOKEN is not set."))
            return

        pending = Video.objects.filter(
            source=Video.Source.STREAM, stream_ready=False
        ).exclude(stream_uid="")

        if not pending:
            self.stdout.write("Nothing pending.")
            return

        ready = 0
        for video in pending:
            data = cloudflare_stream.get_video(video.stream_uid)
            if not data:
                self.stdout.write(f"  {video.name}: not found on Stream")
                continue

            duration = data.get("duration") or 0
            is_ready = (data.get("status") or {}).get("state") == "ready"
            video.duration_seconds = int(duration) if duration > 0 else 0
            video.stream_ready = is_ready
            video.save(update_fields=["duration_seconds", "stream_ready", "modified"])

            ready += is_ready
            state = "listo" if is_ready else (data.get("status") or {}).get("state", "?")
            self.stdout.write(f"  {video.name}: {state}, {video.duration_seconds}s")

        self.stdout.write(
            self.style.SUCCESS(f"\n{ready} of {len(pending)} are now ready.")
        )
