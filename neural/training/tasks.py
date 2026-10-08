"""Tareas de fondo del módulo de videos."""

import logging

from config import celery_app
from neural.services.push_notifications import (
    NotificationPayload,
    PushNotificationService,
)
from neural.training.models import PackageAssignment, VideoPackage
from neural.users.models import PushNotification, UserMembership, User

logger = logging.getLogger(__name__)


def users_reached_by(assignment):
    """A quién le llega esa asignación.

    Las tres vías del modelo: a un socio, a todo un plan, o a todos. Se
    resuelve acá y no en la vista porque un «a todos» son cientos de consultas
    y la persona que asignó no tiene por qué esperarlas.
    """
    if assignment.user_id:
        return User.objects.filter(pk=assignment.user_id)
    if assignment.plan_id:
        ids = UserMembership.objects.filter(
            plan_id=assignment.plan_id, is_active=True
        ).values_list("user_id", flat=True)
        return User.objects.filter(pk__in=ids, is_client=True)
    return User.objects.filter(is_client=True, is_staff=False)


@celery_app.task
def notify_package_assigned(assignment_id):
    """Avisarle al socio que tiene un módulo nuevo.

    Sin esto el módulo espera a que alguien entre a la pestaña por casualidad.
    No se le avisa a quien ya lo tenía: la asignación se crea una sola vez, así
    que reasignar no vuelve a sonar.
    """
    assignment = (
        PackageAssignment.objects.filter(pk=assignment_id)
        .select_related("package")
        .first()
    )
    if assignment is None:
        logger.warning("notify_package_assigned: asignación %s no existe", assignment_id)
        return 0

    package = assignment.package
    # Un módulo sin publicar no le llega a nadie, así que anunciarlo sería
    # mandar al socio a una pestaña donde no hay nada.
    if not package.is_published:
        logger.info("notify_package_assigned: %s sin publicar, no se avisa", package.pk)
        return 0

    destinatarios = list(users_reached_by(assignment))
    if not destinatarios:
        return 0

    cuantos = package.items.count()
    payload = NotificationPayload(
        title="Tenés ejercicios nuevos",
        body=(
            f"{package.name} · {cuantos} "
            f"{'video' if cuantos == 1 else 'videos'} para hacer en casa."
        ),
        # La app usa esto para abrir el módulo en vez de la pantalla de inicio.
        data={"type": "video_package", "package_id": package.pk},
        notification_type=PushNotification.NotificationType.VIDEO_PACKAGE,
    )

    enviados = PushNotificationService.send_to_users(destinatarios, payload)
    logger.info(
        "notify_package_assigned: %s avisos de «%s»", len(enviados), package.name
    )
    return len(enviados)


@celery_app.task
def notify_packages_assigned(assignment_ids):
    """Varias asignaciones de una. Es lo que pasa al elegir seis socios."""
    return sum(notify_package_assigned(pk) for pk in assignment_ids)


__all__ = [
    "notify_package_assigned",
    "notify_packages_assigned",
    "users_reached_by",
    "VideoPackage",
]
