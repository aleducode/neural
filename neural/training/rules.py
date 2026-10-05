"""Who may book a class, and why not.

Booking has never checked the membership: BookTrainingView only asks for a
verified account, no other booking that day, and a free place. In the last 30
days 274 of 1172 confirmed bookings --23%, across 46 people-- were made with no
valid membership for that date.

Turning that into a rule changes who can train tomorrow, so it ships behind
`settings.ENFORCE_MEMBERSHIP_ON_BOOKING`, off by default. With the switch off
`check_booking` still reports what it would have said, which is what the
`membership_debt` command uses to list the people to regularise first.
"""

from django.conf import settings

from neural.users.models import UserMembership

# Lo que ve el socio. Primera persona y con la fecha adentro: "no tienes
# membresia activa" manda a recepcion sin saber que preguntar.
SIN_MEMBRESIA = "No tenemos una membresía activa a tu nombre. Acercate a recepción."
VENCIDA = "Tu plan venció el {fecha}. Acercate a recepción para renovarlo."
SIN_SESIONES = (
    "Ya usaste las {total} sesiones de tu tiquetera. "
    "Vence el {fecha}, pero no quedan sesiones por agendar."
)


def active_membership(user, day):
    """La membresía que cubre ese día, o None.

    Si hay varias --pasa cuando alguien renueva antes de que venza la
    anterior-- gana la que vence más tarde, que es la que el socio
    considera suya.
    """
    candidatas = [
        m
        for m in user.memberships.select_related("plan").all()
        if m.is_valid_on(day)
    ]
    if not candidatas:
        return None
    return max(candidatas, key=lambda m: m.expiration_date or day)


def check_booking(user, day):
    """`(puede, motivo)` para reservar ese día.

    `motivo` es None cuando puede. Se calcula siempre, se aplique o no: el
    informe de quiénes están sin membresía sale de aquí.
    """
    membresia = active_membership(user, day)
    if membresia is None:
        # La ultima que ya vencio. Filtrar por fecha en la consulta y no mirar
        # solo la mas reciente: con una membresia futura desactivada --algo que
        # pasa al renovar-- la mas reciente no esta vencida y el socio recibia
        # "no tenemos membresia a tu nombre" en vez de la fecha en que vencio.
        vencida = (
            user.memberships.filter(expiration_date__lt=day)
            .order_by("-expiration_date")
            .first()
        )
        if vencida:
            return False, VENCIDA.format(fecha=_fecha(vencida.expiration_date))
        return False, SIN_MEMBRESIA

    if membresia.is_ticket_pack and membresia.sessions_left <= 0:
        return False, SIN_SESIONES.format(
            total=membresia.sessions_total,
            fecha=_fecha(membresia.expiration_date),
        )

    return True, None


def enforced():
    """Si el control ya se aplica o sólo se mide."""
    return bool(getattr(settings, "ENFORCE_MEMBERSHIP_ON_BOOKING", False))


MESES = [
    "Ene", "Feb", "Mar", "Abr", "May", "Jun",
    "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
]


def _fecha(value):
    return f"{value.day} {MESES[value.month - 1]} {value.year}"


def membership_summary(user, day):
    """Lo que la app le muestra al socio sobre su plan.

    Es el texto que pidió recepción: hasta cuándo vale y, si es tiquetera,
    cuántas sesiones le quedan.
    """
    membresia = active_membership(user, day)
    if membresia is None:
        return {
            "active": False,
            "plan": None,
            "expiration_date": None,
            "days_left": 0,
            "is_ticket_pack": False,
            "sessions_total": 0,
            "sessions_used": 0,
            "sessions_left": None,
            "message": SIN_MEMBRESIA,
        }

    vence = membresia.expiration_date
    if membresia.is_ticket_pack:
        quedan = membresia.sessions_left
        if quedan:
            mensaje = (
                f"Tu plan tiene vigencia hasta el {_fecha(vence)}. "
                f"Te {'queda' if quedan == 1 else 'quedan'} "
                f"{quedan} {'sesión' if quedan == 1 else 'sesiones'} por agendar."
            )
        else:
            mensaje = SIN_SESIONES.format(
                total=membresia.sessions_total, fecha=_fecha(vence)
            )
    else:
        mensaje = f"Tu plan tiene vigencia hasta el {_fecha(vence)}."

    return {
        "active": True,
        "plan": membresia.plan.name if membresia.plan else None,
        "expiration_date": vence.isoformat() if vence else None,
        "days_left": membresia.days_left if vence else None,
        "is_ticket_pack": membresia.is_ticket_pack,
        "sessions_total": membresia.sessions_total,
        "sessions_used": membresia.sessions_used,
        "sessions_left": membresia.sessions_left,
        "message": mensaje,
    }


def memberships_in_debt(since, until):
    """Quién reservó sin membresía válida en ese rango.

    Lo usa el comando que recepción necesita antes de que el control se
    encienda: la lista de gente a regularizar.
    """
    from neural.training.models import UserTraining

    reservas = (
        UserTraining.objects.filter(
            slot__date__gte=since,
            slot__date__lte=until,
            status=UserTraining.Status.CONFIRMED,
        )
        .select_related("user", "slot")
        .prefetch_related("user__memberships")
    )

    por_usuario = {}
    for reserva in reservas:
        puede, motivo = check_booking(reserva.user, reserva.slot.date)
        if puede:
            continue
        fila = por_usuario.setdefault(
            reserva.user_id,
            {"user": reserva.user, "reservas": 0, "motivo": motivo, "ultima": None},
        )
        fila["reservas"] += 1
        if fila["ultima"] is None or reserva.slot.date > fila["ultima"]:
            fila["ultima"] = reserva.slot.date
    return sorted(por_usuario.values(), key=lambda f: -f["reservas"])


def membership_for_display(user):
    """Atajo para el panel: la membresía de hoy."""
    from django.utils import timezone

    return active_membership(user, timezone.localdate())


__all__ = [
    "active_membership",
    "check_booking",
    "enforced",
    "membership_summary",
    "memberships_in_debt",
    "membership_for_display",
    "UserMembership",
]
