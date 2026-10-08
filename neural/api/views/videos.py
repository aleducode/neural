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

from neural.training.models import (
    PackageAssignment,
    Video,
    VideoPackage,
    VideoProgress,
)
from neural.users.display import display_name
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


def assignments_reaching(user, package_ids):
    """La asignacion mas reciente que le hace llegar cada modulo.

    Mismas tres vias que `assigned_packages`; si dos coinciden --le llega por
    su plan y ademas se lo asignaron a el-- vale la ultima."""
    if not package_ids:
        return {}
    plan_ids = list(
        UserMembership.objects.filter(user=user, is_active=True).values_list(
            "plan_id", flat=True
        )
    )
    filas = (
        PackageAssignment.objects.filter(
            Q(user=user) | Q(plan_id__in=plan_ids) | Q(everyone=True),
            package_id__in=package_ids,
        )
        .select_related("assigned_by")
        .order_by("created")
    )
    # El orden ascendente deja la mas reciente al final, que es la que queda.
    return {fila.package_id: fila for fila in filas}


def serialize_package(package, progress, assignment):
    """Un modulo tal como lo consume la app.

    La usan la lista y el detalle: dos copias de esto se desincronizan en
    cuanto alguien agrega un campo en una sola."""
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
                # hls | youtube | file: con que reproductor se ve.
                "player": video.player,
                "seconds": seen.seconds if seen else 0,
                "completed": bool(seen and seen.completed_at),
            }
        )
    return {
        "id": package.pk,
        "name": package.name,
        "description": package.description,
        "cover": package.cover.url if package.cover else None,
        "kind": package.kind,
        "assigned_at": assignment.created.isoformat() if assignment else None,
        "assigned_by": (
            display_name(assignment.assigned_by)
            if assignment and assignment.assigned_by
            else None
        ),
        "videos": videos,
        "completed": sum(1 for v in videos if v["completed"]),
        "total": len(videos),
    }


def progress_map(user, packages):
    """El progreso del socio, solo de los videos que estan en esos modulos."""
    ids = [item.video_id for p in packages for item in p.items.all()]
    return {
        row.video_id: row
        for row in VideoProgress.objects.filter(user=user, video_id__in=ids)
    }


class MyPackagesView(APIView):
    """The member's packages, with their own progress on each video."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        packages = list(assigned_packages(request.user))
        progress = progress_map(request.user, packages)
        # Cuando y quien se lo asigno. Un modulo puede llegarle por tres vias
        # --a el, a su plan, o a todos-- y puede haber mas de una: gana la mas
        # reciente, que es la que el socio vive como "esto es nuevo".
        reach = assignments_reaching(request.user, [p.pk for p in packages])
        return Response(
            {
                "packages": [
                    serialize_package(p, progress, reach.get(p.pk)) for p in packages
                ]
            }
        )


class PackageDetailView(APIView):
    """Un modulo solo.

    Sin esto, abrir un video se bajaba el catalogo entero --todos los modulos
    con todos sus videos-- para quedarse con uno.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # Se busca dentro de los que le llegan: pedir el id de un modulo ajeno
        # tiene que dar 404, no el modulo.
        package = assigned_packages(request.user).filter(pk=pk).first()
        if package is None:
            return Response(
                {"detail": "Ese módulo no está entre los tuyos."},
                status=status.HTTP_404_NOT_FOUND,
            )
        progress = progress_map(request.user, [package])
        reach = assignments_reaching(request.user, [package.pk])
        return Response(serialize_package(package, progress, reach.get(package.pk)))


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
