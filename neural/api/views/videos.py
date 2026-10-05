"""API views for the video library.

What the mobile app needs: the packages assigned to the signed-in member, and a
way to report how much of each video was watched. That report is what turns the
library into data --without it the panel knows a package was assigned but not
whether anyone watched it.
"""

import logging

from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from neural.training.models import Video, VideoPackage, VideoProgress
from neural.users.models import UserMembership

logger = logging.getLogger(__name__)

# Below this, a video counts as finished. Players rarely reach the exact end:
# credits, a pause, or the app closing a second early would otherwise leave
# everything stuck at 97%.
COMPLETE_AT = 0.95


def assigned_packages(user):
    """Published packages that reach this member.

    Three routes --assigned to them, to their plan, or to everyone-- and a
    package must appear once even when two routes apply.
    """
    plan_ids = list(
        UserMembership.objects.filter(user=user, is_active=True).values_list(
            "plan_id", flat=True
        )
    )
    return (
        VideoPackage.objects.filter(
            Q(assignments__user=user)
            | Q(assignments__plan_id__in=plan_ids)
            | Q(assignments__everyone=True),
            is_published=True,
        )
        .distinct()
        .prefetch_related("items__video")
    )


class MyPackagesView(APIView):
    """The member's packages, with their own progress on each video."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        packages = assigned_packages(request.user)
        progress = {
            row.video_id: row
            for row in VideoProgress.objects.filter(user=request.user)
        }

        payload = []
        for package in packages:
            videos = []
            for item in package.items.all():
                video = item.video
                seen = progress.get(video.pk)
                videos.append(
                    {
                        "id": video.pk,
                        "name": video.name,
                        "description": video.description,
                        "notes": item.notes,
                        "order": item.order,
                        "duration": video.duration_seconds,
                        "poster": video.poster,
                        "playback": video.playback,
                        "embed": video.embed,
                        "source": video.source,
                        "seconds": seen.seconds if seen else 0,
                        "completed": bool(seen and seen.completed_at),
                    }
                )
            done = sum(1 for v in videos if v["completed"])
            payload.append(
                {
                    "id": package.pk,
                    "name": package.name,
                    "description": package.description,
                    "cover": package.cover.url if package.cover else None,
                    "kind": package.kind,
                    "videos": videos,
                    "completed": done,
                    "total": len(videos),
                }
            )
        return Response({"packages": payload})


class VideoProgressView(APIView):
    """Reports how far into a video the member got.

    The app posts this while playing, so it must be cheap and idempotent: one
    row per member and video, updated in place.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            video_id = int(request.data.get("video_id"))
            seconds = int(request.data.get("seconds", 0))
        except (TypeError, ValueError):
            return Response(
                {"detail": "video_id y seconds son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        video = Video.objects.filter(pk=video_id).first()
        if not video:
            return Response(
                {"detail": "Ese video no existe."}, status=status.HTTP_404_NOT_FOUND
            )

        # A member can only report progress on a video they actually receive:
        # otherwise the panel's numbers could be inflated from outside.
        reachable = Video.objects.filter(
            pk=video_id, packages__in=assigned_packages(request.user)
        ).exists()
        if not reachable:
            return Response(
                {"detail": "Ese video no está en tus paquetes."},
                status=status.HTTP_403_FORBIDDEN,
            )

        row, _ = VideoProgress.objects.get_or_create(user=request.user, video=video)
        # Never go backwards: scrubbing to the start should not erase that the
        # member already watched the whole thing.
        row.seconds = max(row.seconds, max(seconds, 0))
        if (
            not row.completed_at
            and video.duration_seconds
            and row.seconds >= video.duration_seconds * COMPLETE_AT
        ):
            row.completed_at = timezone.now()
        row.save(update_fields=["seconds", "completed_at", "modified"])

        return Response(
            {
                "video_id": video.pk,
                "seconds": row.seconds,
                "percent": row.percent,
                "completed": bool(row.completed_at),
            }
        )
