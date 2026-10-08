"""Dashboard metrics for the manager panel.

Every widget comes from a real Neural model. What the design asks for and
Neural does not have --trainers, payment method, class photo-- is never made
up: it is replaced by the data that does exist, and the label says so."""

from collections import OrderedDict
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Count, Max, Prefetch, Q, Sum
from django.templatetags.static import static
from django.utils import timezone

from neural.training.models import (
    Classes,
    Slot,
    TrainingType,
    UserTraining,
    Video,
    VideoPackage,
    VideoProgress,
)
from neural.users.models import (
    Device,
    NeuralPlan,
    Profile,
    Ranking,
    User,
    UserMembership,
    PushNotification,
    PushNotificationLog,
    UserPaymentReference,
    UserStats,
    UserStrike,
    UserWeight,
)
from neural.users.display import display_name, initials, photo_url

MESES = [
    "Ene", "Feb", "Mar", "Abr", "May", "Jun",
    "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
]
MESES_LARGOS = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

# Cancelled bookings are neither attendance nor demand.
ACTIVAS = ~Q(status=UserTraining.Status.CANCELLED)


def client_users():
    """The real members.

    Staff excluded: internal accounts carry is_client=True and were inflating
    the total."""
    return User.objects.filter(is_client=True, is_staff=False)


def assignable_users():
    """A quien se le puede asignar un modulo.

    Incluye al equipo, a diferencia de `client_users()`: la gente del gimnasio
    tambien entrena, y excluirla dejaba al dueno sin poder asignarse un modulo
    a si mismo para probarlo. Las metricas siguen usando `client_users()`, que
    no los cuenta --para eso se separaron."""
    return User.objects.filter(is_client=True)


def pct_change(current, previous):
    """Percent change, or None when there is no baseline to measure against.

    Returning 0 when the previous period was 0 would read as "nothing changed",
    which is the exact opposite of what happened."""
    if not previous:
        return None
    return round(((current - previous) / previous) * 100, 1)


def month_start(reference, months_back=0):
    """First day of the month, `months_back` months before `reference`."""
    year, month = reference.year, reference.month - months_back
    while month <= 0:
        month += 12
        year -= 1
    return date(year, month, 1)


def _money(value):
    return int(value or 0)


def kpis(today):
    """The four widgets at the top.

    The design asks for «Active Trainers». Neural has no trainer model, so that
    slot shows active memberships instead: it exists, and it answers the same
    business question --how much of the operation is alive today."""
    this_month = month_start(today)
    last_month = month_start(today, 1)
    dia_del_mes = today.day

    total_users = client_users().count()
    # The total a month ago = today's minus everyone who signed up since
    # then. Nobody is deleted, so the subtraction is exact.
    altas_este_mes = client_users().filter(date_joined__date__gte=this_month).count()
    usuarios_mes_pasado = total_users - altas_este_mes

    payments = UserPaymentReference.objects.filter(is_paid=True)
    month_revenue = payments.filter(created__date__gte=this_month).aggregate(
        total=Sum("amount")
    )["total"] or Decimal(0)
    # Same stretch of last month, not the whole month: comparing 5 days to 31
    # draws a drop that does not exist.
    previous_revenue = payments.filter(
        created__date__gte=last_month,
        created__date__lt=last_month + timedelta(days=dia_del_mes),
    ).aggregate(total=Sum("amount"))["total"] or Decimal(0)

    memberships = UserMembership.objects.filter(is_active=True).count()
    previous_memberships = UserMembership.objects.filter(
        is_active=True, created__date__lt=this_month
    ).count()

    checkins = UserTraining.objects.filter(slot__date=today).filter(ACTIVAS).count()
    # Against the same weekday last week: a Tuesday is not comparable to a
    # Sunday.
    checkins_previos = (
        UserTraining.objects.filter(slot__date=today - timedelta(days=7))
        .filter(ACTIVAS)
        .count()
    )

    return [
        {
            "key": "usuarios",
            "icon": "users",
            "label": "Total usuarios",
            "value": f"{total_users:,}".replace(",", "."),
            "delta": pct_change(total_users, usuarios_mes_pasado),
            "basis": "frente al cierre del mes pasado",
        },
        {
            "key": "ingresos",
            "icon": "wallet",
            "label": "Ingresos del mes",
            "value": f"$ {_money(month_revenue):,}".replace(",", "."),
            "delta": pct_change(_money(month_revenue), _money(previous_revenue)),
            "basis": f"frente a los primeros {dia_del_mes} días del mes pasado",
        },
        {
            "key": "membresias",
            "icon": "badge-check",
            "label": "Membresías activas",
            "value": f"{memberships:,}".replace(",", "."),
            "delta": pct_change(memberships, previous_memberships),
            "basis": "frente al cierre del mes pasado",
        },
        {
            "key": "checkins",
            "icon": "scan-line",
            "label": "Check-ins de hoy",
            "value": str(checkins),
            "delta": pct_change(checkins, checkins_previos),
            "basis": "frente al mismo día de la semana pasada",
        },
    ]


def growth(today, months=12):
    """Month by month growth: new members against members who trained.

    Two series in the same unit (people) on a single axis. They are not different
    scales, so they can share one chart without lying."""
    start = month_start(today, months - 1)
    buckets = OrderedDict()
    for i in range(months):
        m = month_start(today, months - 1 - i)
        buckets[(m.year, m.month)] = {"label": MESES[m.month - 1], "newUsers": 0, "activeUsers": 0}

    signups = (
        client_users()
        .filter(date_joined__date__gte=start)
        .values_list("date_joined", flat=True)
    )
    for signup in signups:
        key = (timezone.localtime(signup).year, timezone.localtime(signup).month)
        if key in buckets:
            buckets[key]["newUsers"] += 1

    # An active user is someone who booked and did not cancel. Counted once
    # per month, not once per booking.
    seen = {key: set() for key in buckets}
    bookings = (
        UserTraining.objects.filter(slot__date__gte=start)
        .filter(ACTIVAS)
        .values_list("slot__date", "user_id")
    )
    for booked_on, user_id in bookings:
        key = (booked_on.year, booked_on.month)
        if key in seen:
            seen[key].add(user_id)
    for key, users in seen.items():
        buckets[key]["activeUsers"] = len(users)

    points = list(buckets.values())
    new_counts = [p["newUsers"] for p in points]
    first = month_start(today, months - 1)
    return {
        "points": points,
        "total": sum(new_counts),
        "delta": pct_change(new_counts[-1], new_counts[0]),
        "range": (
            f"de {MESES_LARGOS[first.month - 1]} a {MESES_LARGOS[today.month - 1]}"
        ),
        "series": [
            {"key": "newUsers", "label": "Usuarios nuevos"},
            {"key": "activeUsers", "label": "Usuarios que entrenaron"},
        ],
    }


# Fallback photos until the gym uploads its own from the admin. Chosen by
# id, not by rank position, so a class keeps its photo whether it moves up
# or down the list.
FOTOS_POR_DEFECTO = [
    "manager/img/classes/fuerza.jpg",
    "manager/img/classes/cardio.jpg",
    "manager/img/classes/movilidad.jpg",
]


def class_photo(training_type):
    """The training type's uploaded photo, or the fallback one."""
    if training_type.photo:
        try:
            return training_type.photo.url
        except ValueError:
            pass
    return static(FOTOS_POR_DEFECTO[training_type.pk % len(FOTOS_POR_DEFECTO)])


def popular_classes(today, days=30, limit=3):
    """The most booked classes over the last `days` days.

    The design shows a photo and a price per class. Neural already has the photo
    (TrainingType.photo); it has no per-class price, so where the design puts the
    price we show the real duration of its schedules and how many bookings it got."""
    since = today - timedelta(days=days)
    # A Count filter resolves against the queryset root, not against the
    # path being counted: the status needs its full path or Django looks for
    # TrainingType.status and blows up.
    kinds = (
        TrainingType.objects.annotate(
            bookings=Count(
                "classes__slots__user_trainings",
                filter=Q(
                    classes__slots__date__gte=since,
                    classes__slots__date__lte=today,
                )
                & ~Q(
                    classes__slots__user_trainings__status=(
                        UserTraining.Status.CANCELLED
                    )
                ),
                distinct=True,
            )
        )
        .filter(bookings__gt=0)
        .order_by("-bookings")[:limit]
    )

    out = []
    for kind in kinds:
        horario = kind.classes.first()
        minutes = None
        if horario:
            start = horario.hour_init.hour * 60 + horario.hour_init.minute
            end = horario.hour_end.hour * 60 + horario.hour_end.minute
            minutes = end - start
        out.append(
            {
                "id": kind.pk,
                "name": kind.name,
                "kind": "Clase grupal" if kind.is_group else "Entrenamiento individual",
                "image": class_photo(kind),
                "duration": f"{minutes} min" if minutes and minutes > 0 else None,
                "bookings": kind.bookings,
            }
        )
    return out


def revenue_by_plan(today, months=12):
    """Donut: how much each plan contributed over the last `months` months.

    A single hue in three steps, most to least. It is a partition of one total,
    not independent categories."""
    since = month_start(today, months - 1)
    rows = (
        UserPaymentReference.objects.filter(is_paid=True, created__date__gte=since)
        .values("plan__id", "plan__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    segmentos = [
        {
            "id": row["plan__id"],
            "label": row["plan__name"] or "Sin plan",
            "value": _money(row["total"]),
        }
        for row in rows
        if _money(row["total"]) > 0
    ]
    total = sum(s["value"] for s in segmentos)
    for segmento in segmentos:
        segmento["share"] = round((segmento["value"] / total) * 100, 1) if total else 0
        segmento["amount"] = f"$ {segmento['value']:,}".replace(",", ".")

    return {
        "segments": segmentos,
        "total": f"$ {total:,}".replace(",", "."),
        "period": f"últimos {months} meses",
    }


def recent_payments(limit=6):
    """Latest payments.

    El diseño pedía una columna «medio de pago». Antes no existía el dato
    --todo pasaba por Bold-- pero ahora recepción registra sus cobros, que son
    la mayoría, y la columna tiene sentido."""
    payments = (
        UserPaymentReference.objects.select_related("user", "user__profile", "plan")
        .order_by("-created")[:limit]
    )
    out = []
    for pago in payments:
        created_at = timezone.localtime(pago.created)
        out.append(
            {
                "id": pago.pk,
                "userId": pago.user_id,
                "reference": pago.reference[:12].upper(),
                "name": display_name(pago.user) or "Sin nombre",
                "initials": initials(pago.user),
                "photo": photo_url(pago.user),
                "plan": pago.plan.name if pago.plan else "Sin plan",
                "method": (
                    "Recepción"
                    if (pago.data or {}).get("method") == "recepcion"
                    else "En línea"
                ),
                "amount": f"$ {_money(pago.amount):,}".replace(",", "."),
                "date": f"{created_at.day} {MESES[created_at.month - 1]} {created_at.year}",
                "paid": pago.is_paid,
                "status": "Pagado" if pago.is_paid else "Pendiente",
            }
        )
    return out


def no_data_notice():
    """What the panel cannot show yet, so it can say so instead of faking it."""
    faltantes = []
    if not NeuralPlan.objects.exists():
        faltantes.append("no hay planes cargados")
    if not UserPaymentReference.objects.filter(is_paid=True).exists():
        faltantes.append("todavía no hay pagos confirmados")
    return faltantes


# ---------------------------------------------------------------------------
# List screens. Each one is the same anatomy from the .pen --header, four
# KPIs, a table card with search, pagination-- over a different model.
# ---------------------------------------------------------------------------

DIAS_ORDEN = [
    Classes.DaysChoices.MONDAY,
    Classes.DaysChoices.TUESDAY,
    Classes.DaysChoices.WEDNESDAY,
    Classes.DaysChoices.THURSDAY,
    Classes.DaysChoices.FRIDAY,
    Classes.DaysChoices.SATURDAY,
    Classes.DaysChoices.SUNDAY,
]

DIAS_CORTOS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


def _fecha(value):
    """3 Oct 2026, or None. The frontend does not format dates: it has no timezone."""
    if not value:
        return None
    return f"{value.day} {MESES[value.month - 1]} {value.year}"


def _hora(value):
    return value.strftime("%H:%M") if value else None


def _kpi(key, icon, label, value, delta, basis):
    return {
        "key": key,
        "icon": icon,
        "label": label,
        "value": value if isinstance(value, str) else f"{value:,}".replace(",", "."),
        "delta": delta,
        "basis": basis,
    }


def members_page(today):
    """Members: the «14. Member - List View» screen.

    The design has an «MB-00124» column. Neural has no member code, so the line
    under the name shows the email, which is the system's real identifier."""
    this_month = month_start(today)
    last_month = month_start(today, 1)
    en_una_semana = today + timedelta(days=7)

    base = client_users()
    active = UserMembership.objects.filter(is_active=True)

    total = base.count()
    with_membership = active.filter(user__in=base).count()
    expiring = active.filter(
        user__in=base, expiration_date__gte=today, expiration_date__lte=en_una_semana
    ).count()
    new_users = base.filter(date_joined__date__gte=this_month).count()
    previous_new_users = base.filter(
        date_joined__date__gte=last_month,
        date_joined__date__lt=last_month + timedelta(days=today.day),
    ).count()

    filas_usuarios = (
        base.select_related("profile")
        .prefetch_related(
            Prefetch("memberships", queryset=active.select_related("plan"), to_attr="vigentes")
        )
        .annotate(
            # ACTIVE resolves against User, not UserTraining: inside an
            # aggregate the status needs its full path.
            ultimo_checkin=Max(
                "trainings__slot__date",
                filter=~Q(trainings__status=UserTraining.Status.CANCELLED),
            ),
        )
        .order_by("-date_joined")
    )

    rows = []
    for i, user in enumerate(filas_usuarios, start=1):
        membership = user.vigentes[0] if user.vigentes else None
        expires = membership.expiration_date if membership else None
        if not membership:
            state, tone = "Sin membresía", "neutral"
        elif expires and expires < today:
            state, tone = "Vencida", "error"
        elif expires and expires <= en_una_semana:
            state, tone = "Por vencer", "warning"
        else:
            state, tone = "Activa", "success"

        rows.append(
            {
                "no": i,
                "id": user.pk,
                "name": display_name(user) or "Sin nombre",
                "initials": initials(user),
                "photo": photo_url(user),
                "email": user.email,
                "phone": user.phone_number or "—",
                "plan": membership.plan.name if membership and membership.plan else "—",
                "status": state,
                "tone": tone,
                "joined": _fecha(timezone.localtime(user.date_joined).date()),
                "expires": _fecha(expires),
                "lastCheckin": _fecha(user.ultimo_checkin) or "Nunca",
            }
        )

    return {
        "kpis": [
            _kpi("total", "users", "Total usuarios", total, None, ""),
            _kpi("active", "badge-check", "Con membresía", with_membership, None, ""),
            _kpi("expiring", "calendar-clock", "Vencen en 7 días", expiring, None, ""),
            _kpi(
                "nuevos",
                "user-plus",
                "Nuevos este mes",
                new_users,
                pct_change(new_users, previous_new_users),
                f"frente a los primeros {today.day} días del mes pasado",
            ),
        ],
        "rows": rows,
    }


def classes_page(today):
    """Classes: the «19. Class - List View» screen.

    The design asks for trainer and level. Neural stores neither, so those columns
    are taken by the day and the time slot, which is what the gym actually manages."""
    since = today - timedelta(days=30)
    today_weekday = DIAS_ORDEN[today.weekday()]

    schedules = (
        Classes.objects.select_related("training_type")
        .annotate(
            bookings=Count(
                "slots__user_trainings",
                filter=Q(slots__date__gte=since, slots__date__lte=today)
                & ~Q(slots__user_trainings__status=UserTraining.Status.CANCELLED),
                distinct=True,
            ),
            places=Max("slots__max_places", filter=Q(slots__date__gte=since)),
        )
    )
    # order_by("day") sorts the string: FRIDAY, MONDAY, SATURDAY... Weekday
    # order is not in the database, so it is applied here over 18 rows.
    order = {dia: i for i, dia in enumerate(DIAS_ORDEN)}
    schedules = sorted(schedules, key=lambda c: (order.get(c.day, 9), c.hour_init))

    # Sessions and places per schedule in a separate query: inside the same
    # annotate as the bookings Count, the max_places Sum would be multiplied
    # by the user_trainings rows.
    capacity = {
        row["class_training_id"]: row
        for row in Slot.objects.filter(date__gte=since, date__lte=today)
        .values("class_training_id")
        .annotate(sessions=Count("id"), places=Sum("max_places"))
    }

    slots_hoy = Slot.objects.filter(date=today)
    places_today = slots_hoy.aggregate(total=Sum("max_places"))["total"] or 0
    rows = []
    for i, klass in enumerate(schedules, start=1):
        start = klass.hour_init.hour * 60 + klass.hour_init.minute
        end = klass.hour_end.hour * 60 + klass.hour_end.minute
        minutes = end - start
        cap = capacity.get(klass.pk, {})
        period_places = cap.get("places") or 0
        occupancy = (
            round((klass.bookings / period_places) * 100) if period_places else None
        )
        rows.append(
            {
                "no": i,
                "id": klass.pk,
                "sessions": cap.get("sessions", 0),
                "occupancy": occupancy,
                "name": klass.training_type.name,
                "typeId": klass.training_type_id,
                "kind": "Grupal" if klass.training_type.is_group else "Individual",
                "day": klass.get_day_display(),
                "isToday": klass.day == today_weekday,
                "time": f"{_hora(klass.hour_init)} – {_hora(klass.hour_end)}",
                "duration": f"{minutes} min" if minutes > 0 else "—",
                "places": klass.places or 0,
                "bookings": klass.bookings,
            }
        )

    with_occupancy = [f["occupancy"] for f in rows if f["occupancy"] is not None]
    average = round(sum(with_occupancy) / len(with_occupancy)) if with_occupancy else 0
    return {
        "kpis": [
            _kpi("schedules", "calendar-days", "Horarios activos", len(rows), None, ""),
            _kpi(
                "hoy",
                "calendar-clock",
                "Clases de hoy",
                sum(1 for f in rows if f["isToday"]),
                None,
                "",
            ),
            _kpi("places", "users", "Cupos de hoy", places_today, None, ""),
            _kpi(
                "ocupacion",
                "flame",
                "Ocupación promedio (30 días)",
                f"{average}%",
                None,
                "",
            ),
        ],
        "rows": rows,
    }


def bookings_page(today, days=30):
    """Bookings: the «22. Booking - List View» screen.

    A `days`-wide window is sent, not the whole table: there are tens of thousands
    of historical rows and the screen says which period it covers."""
    since = today - timedelta(days=days)
    until = today + timedelta(days=days)

    bookings = (
        UserTraining.objects.filter(slot__date__gte=since, slot__date__lte=until)
        .select_related("user", "user__profile", "slot", "slot__class_training__training_type")
        .order_by("-slot__date", "-created")
    )

    ETIQUETA = {
        UserTraining.Status.CONFIRMED: ("Confirmada", "success"),
        UserTraining.Status.DONE: ("Terminada", "neutral"),
        UserTraining.Status.CANCELLED: ("Cancelada", "error"),
    }

    rows = []
    for reserva in bookings:
        klass = reserva.slot.class_training
        label, tone = ETIQUETA.get(reserva.status, (reserva.status, "neutral"))
        rows.append(
            {
                "id": reserva.pk,
                "userId": reserva.user_id,
                "reference": f"RS-{reserva.pk:05d}",
                "name": display_name(reserva.user) or "Sin nombre",
                "initials": initials(reserva.user),
                "photo": photo_url(reserva.user),
                "email": reserva.user.email,
                "klass": klass.training_type.name if klass else "Sin clase",
                "date": _fecha(reserva.slot.date),
                "isToday": reserva.slot.date == today,
                "time": f"{_hora(klass.hour_init)} – {_hora(klass.hour_end)}" if klass else "—",
                "status": label,
                "tone": tone,
            }
        )

    hoy = UserTraining.objects.filter(slot__date=today).filter(ACTIVAS).count()
    hoy_semana_pasada = (
        UserTraining.objects.filter(slot__date=today - timedelta(days=7))
        .filter(ACTIVAS)
        .count()
    )
    upcoming = (
        UserTraining.objects.filter(
            slot__date__gt=today, slot__date__lte=today + timedelta(days=7)
        )
        .filter(ACTIVAS)
        .count()
    )
    cancelled = UserTraining.objects.filter(
        slot__date__gte=since,
        slot__date__lte=today,
        status=UserTraining.Status.CANCELLED,
    ).count()
    del_periodo = UserTraining.objects.filter(
        slot__date__gte=since, slot__date__lte=today
    ).count()

    return {
        "kpis": [
            _kpi(
                "hoy",
                "scan-line",
                "Reservas de hoy",
                hoy,
                pct_change(hoy, hoy_semana_pasada),
                "frente al mismo día de la semana pasada",
            ),
            _kpi("upcoming", "calendar-clock", "Próximos 7 días", upcoming, None, ""),
            _kpi("cancelled", "circle-x", "Canceladas (30 días)", cancelled, None, ""),
            _kpi(
                "tasa",
                "percent",
                "Tasa de cancelación",
                f"{round((cancelled / del_periodo) * 100) if del_periodo else 0}%",
                None,
                "",
            ),
        ],
        "rows": rows,
        "period": f"del {_fecha(since)} al {_fecha(until)}",
    }


def calendar_month(today, year=None, month=None):
    """Calendar: the «23. Calendar View - Month» screen.

    A grid of whole weeks (Monday to Sunday) with each day's classes."""
    year = year or today.year
    month = month or today.month
    first = date(year, month, 1)
    next_month = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

    # The grid starts on the Monday of day 1's week and ends on the Sunday
    # of the last day's week: always whole weeks.
    start = first - timedelta(days=first.weekday())
    last_error = next_month - timedelta(days=1)
    end = last_error + timedelta(days=6 - last_error.weekday())

    slots = (
        Slot.objects.filter(date__gte=start, date__lte=end)
        .select_related("class_training__training_type")
        .annotate(
            taken=Count(
                "user_trainings",
                filter=~Q(user_trainings__status=UserTraining.Status.CANCELLED),
                distinct=True,
            )
        )
        .order_by("date", "class_training__hour_init")
    )

    by_day = {}
    for slot in slots:
        klass = slot.class_training
        if not klass:
            continue
        by_day.setdefault(slot.date, []).append(
            {
                "id": slot.pk,
                "name": klass.training_type.name,
                "time": _hora(klass.hour_init),
                "taken": slot.taken,
                "places": slot.max_places,
                "full": slot.taken >= slot.max_places,
            }
        )

    days = []
    cursor = start
    while cursor <= end:
        days.append(
            {
                "date": cursor.isoformat(),
                "day": cursor.day,
                "inMonth": cursor.month == month,
                "isToday": cursor == today,
                "classes": by_day.get(cursor, []),
            }
        )
        cursor += timedelta(days=1)

    previous = month_start(first, 1)
    return {
        "title": f"{MESES_LARGOS[month - 1].capitalize()} {year}",
        "year": year,
        "month": month,
        "weekdays": DIAS_CORTOS,
        "days": days,
        "prev": {"year": previous.year, "month": previous.month},
        "next": {"year": next_month.year, "month": next_month.month},
        "today": {"year": today.year, "month": today.month},
    }


def _es_recepcion(pago):
    return (pago.data or {}).get("method") == "recepcion"


def unpaid_attempts(today, days=90, limit=30):
    """Quién quiso pagar en la app y no pudo, agrupado por persona.

    La app genera la referencia y ahí se corta: el checkout de Bold nunca se
    construyó. Así que estas filas no son abandonos, son gente que intentó
    pagar contra una pared. Agrupadas por persona, porque el mismo socio
    reintenta --hay uno con 26-- y verlo 26 veces no dice nada.
    """
    desde = today - timedelta(days=days)
    filas = {}
    intentos = (
        UserPaymentReference.objects.filter(is_paid=False, created__date__gte=desde)
        .select_related("user", "user__profile", "plan")
        .order_by("created")
    )
    for intento in intentos:
        fila = filas.setdefault(
            intento.user_id,
            {
                "id": intento.user_id,
                "name": display_name(intento.user) or intento.user.email,
                "initials": initials(intento.user),
                "photo": photo_url(intento.user),
                "email": intento.user.email,
                "phone": intento.user.phone_number or "",
                "plan": intento.plan.name if intento.plan else "Sin plan",
                "attempts": 0,
                "last": None,
            },
        )
        fila["attempts"] += 1
        fila["last"] = _fecha(timezone.localtime(intento.created).date())

    # Quien ya tiene membresia se canso y fue a recepcion: no hay plata
    # perdida, hay una molestia. Quien no la tiene, no esta entrenando.
    activos = set(
        UserMembership.objects.filter(
            user_id__in=filas, is_active=True
        ).values_list("user_id", flat=True)
    )
    for uid, fila in filas.items():
        fila["solved"] = uid in activos

    ordenadas = sorted(
        filas.values(), key=lambda f: (f["solved"], -f["attempts"])
    )
    return ordenadas[:limit]


def payments_page(today, limit=400):
    """Pagos: la plata que entró, por dónde entró, y quién quiso pagar y no pudo.

    Antes la pantalla listaba referencias de pago, que son intenciones y no
    cobros: 754 sin pagar contra 66 pagadas. Mostraba el 5% del ingreso real
    del gimnasio, porque lo que cobra recepción no pasaba por acá.
    """
    this_month = month_start(today)
    last_month = month_start(today, 1)

    cobros = list(
        UserPaymentReference.objects.filter(
            is_paid=True, created__date__gte=this_month
        ).select_related("plan")
    )
    recepcion = [p for p in cobros if _es_recepcion(p)]
    online = [p for p in cobros if not _es_recepcion(p)]

    total = sum(int(p.amount) for p in cobros)
    previo = int(
        UserPaymentReference.objects.filter(
            is_paid=True,
            created__date__gte=last_month,
            created__date__lt=last_month + timedelta(days=today.day),
        ).aggregate(t=Sum("amount"))["t"]
        or 0
    )

    atascados = unpaid_attempts(today)
    sin_resolver = [f for f in atascados if not f["solved"]]

    def plata(valor):
        return f"$ {valor:,}".replace(",", ".")

    return {
        "kpis": [
            _kpi(
                "ingresos",
                "wallet",
                "Ingresos del mes",
                plata(total),
                pct_change(total, previo),
                f"frente a los primeros {today.day} días del mes pasado",
            ),
            _kpi(
                "recepcion",
                "receipt",
                "Cobrado en recepción",
                plata(sum(int(p.amount) for p in recepcion)),
                None,
                f"{len(recepcion)} {'cobro' if len(recepcion) == 1 else 'cobros'}",
            ),
            _kpi(
                "online",
                "badge-check",
                "Cobrado en línea",
                plata(sum(int(p.amount) for p in online)),
                None,
                f"{len(online)} {'cobro' if len(online) == 1 else 'cobros'}",
            ),
            _kpi(
                "atascados",
                "circle-x",
                "Quisieron pagar y no pudieron",
                len(sin_resolver),
                None,
                "sin membresía, últimos 90 días",
            ),
        ],
        "rows": recent_payments(limit=limit),
        "attempts": atascados,
        "attemptsTotal": UserPaymentReference.objects.filter(is_paid=False).count(),
        # La separacion por canal arranca hoy: antes recepcion no registraba
        # nada, asi que los meses viejos figuran enteros como "en linea".
        "sinceNote": (
            "Los cobros de recepción se registran desde que el panel los pide "
            "al activar un plan. Lo anterior a eso no está acá."
        ),
    }


def plans_page(today, months=12):
    """Plans: the «30. Settings - Plan» screen, read as a catalogue."""
    since = month_start(today, months - 1)

    # Counting memberships and summing payments in one query multiplies the
    # sum by the other JOIN's rows: with 5 memberships and 3 payments the
    # the Sum returned $1,800,000 instead of $360,000. distinct=True fixes the
    # Count but not the Sum, so each aggregate gets its own query.
    revenue_by_plan_id = dict(
        UserPaymentReference.objects.filter(is_paid=True, created__date__gte=since)
        .values_list("plan_id")
        .annotate(total=Sum("amount"))
    )
    usuarios_por_plan = dict(
        UserMembership.objects.filter(is_active=True)
        .values_list("plan_id")
        .annotate(total=Count("id"))
    )

    plans = NeuralPlan.objects.order_by("duration", "price")

    rows = []
    for plan in plans:
        revenue = _money(revenue_by_plan_id.get(plan.pk))
        plan.users = usuarios_por_plan.get(plan.pk, 0)
        rows.append(
            {
                "id": plan.pk,
                "name": plan.name,
                "description": plan.description,
                "price": f"$ {_money(plan.price):,}".replace(",", "."),
                "duration": f"{plan.duration} días",
                "perMonth": f"$ {round(_money(plan.price) / max(plan.duration / 30, 1)):,}".replace(
                    ",", "."
                ),
                # Crudos, para el formulario de edicion.
                "priceRaw": int(plan.price),
                "durationDays": plan.duration,
                "sessions": plan.sessions,
                "members": plan.users,
                "revenue": f"$ {revenue:,}".replace(",", "."),
                "revenueRaw": revenue,
            }
        )

    total_users = sum(f["members"] for f in rows)
    total_revenue = sum(f["revenueRaw"] for f in rows)
    for row in rows:
        row["share"] = (
            round((row["members"] / total_users) * 100, 1) if total_users else 0
        )

    best_selling = max(rows, key=lambda f: f["members"], default=None)
    return {
        "kpis": [
            _kpi("plans", "layers", "Planes en catálogo", len(rows), None, ""),
            _kpi("users", "badge-check", "Membresías activas", total_users, None, ""),
            _kpi(
                "recaudado",
                "wallet",
                f"Recaudado ({months} meses)",
                f"$ {total_revenue:,}".replace(",", "."),
                None,
                "",
            ),
            _kpi(
                "top",
                "trophy",
                "Plan más vendido",
                best_selling["name"] if best_selling else "—",
                None,
                "",
            ),
        ],
        "rows": rows,
    }


# ---------------------------------------------------------------------------
# Detail screens. Both follow the same mould from the .pen: a header with
# identity, four KPIs, an editable record and the history on the sides.
# ---------------------------------------------------------------------------


def _iso_weeks(today, count):
    """The last `count` ISO weeks, oldest first."""
    weeks = []
    cursor = today - timedelta(days=today.weekday())
    for _ in range(count):
        iso = cursor.isocalendar()
        weeks.append((iso[0], iso[1], cursor))
        cursor -= timedelta(days=7)
    return list(reversed(weeks))


def plan_choices():
    """Los planes que recepción puede activar, con lo que el panel necesita
    mostrar antes de confirmar: cuánto dura y cuántas sesiones trae."""
    return [
        {
            "value": str(p.pk),
            "label": p.name,
            "days": p.duration,
            "sessions": p.sessions,
            "price": f"$ {_money(p.price):,}".replace(",", ".") if p.price else None,
            "priceRaw": int(p.price),
        }
        for p in NeuralPlan.objects.order_by("sessions", "duration")
    ]


def member_detail(user_id, today):
    """«41. Member - Detail 360»: everything Neural knows about a member."""
    user = (
        client_users()
        .select_related("profile")
        .prefetch_related("memberships__plan")
        .get(pk=user_id)
    )
    profile = Profile.objects.filter(user=user).first()

    bookings = UserTraining.objects.filter(user=user).filter(ACTIVAS)
    total_entrenos = bookings.count()
    streak = (
        UserStrike.objects.filter(user=user, is_current=True)
        .order_by("-weeks")
        .first()
    )
    ranking = Ranking.objects.filter(user=user).order_by("position").first()
    weights = list(UserWeight.objects.filter(user=user).order_by("-created")[:6])
    current_weight = weights[0].weight if weights else None

    membership = next((m for m in user.memberships.all() if m.is_active), None)
    expires = membership.expiration_date if membership else None
    days_left = (expires - today).days if expires else None
    duration = membership.plan.duration if membership and membership.plan else None
    elapsed = (
        max(duration - days_left, 0)
        if duration is not None and days_left is not None
        else None
    )

    if not membership:
        state, tone = "Sin membresía", "neutral"
    elif days_left is not None and days_left < 0:
        state, tone = "Vencida", "error"
    elif days_left is not None and days_left <= 7:
        state, tone = "Por vencer", "warning"
    else:
        state, tone = "Activa", "success"

    # Weeks come from UserStats, which the mobile app already feeds.
    weeks = _iso_weeks(today, 12)
    stats = {
        (s.year, s.week): s.trainings
        for s in UserStats.objects.filter(
            user=user, year__in={a for a, _, _ in weeks}
        )
    }
    weekly = [
        {"label": str(week), "value": stats.get((year, week), 0)}
        for year, week, _ in weeks
    ]

    ETIQUETA = {
        UserTraining.Status.CONFIRMED: ("Confirmada", "success"),
        UserTraining.Status.DONE: ("Terminada", "neutral"),
        UserTraining.Status.CANCELLED: ("Cancelada", "error"),
    }
    activity = []
    for r in (
        UserTraining.objects.filter(user=user)
        .select_related("slot", "slot__class_training__training_type")
        .order_by("-slot__date")[:8]
    ):
        klass = r.slot.class_training
        label, row_tone = ETIQUETA.get(r.status, (r.status, "neutral"))
        activity.append(
            {
                "id": r.pk,
                "date": _fecha(r.slot.date),
                "klass": klass.training_type.name if klass else "Sin clase",
                "time": f"{_hora(klass.hour_init)} – {_hora(klass.hour_end)}" if klass else "—",
                "status": label,
                "tone": row_tone,
            }
        )

    payments = []
    for p in UserPaymentReference.objects.filter(user=user).select_related("plan").order_by("-created")[:10]:
        created_at = timezone.localtime(p.created)
        payments.append(
            {
                "id": p.pk,
                "reference": p.reference[:12].upper(),
                "plan": p.plan.name if p.plan else "Sin plan",
                "amount": f"$ {_money(p.amount):,}".replace(",", "."),
                "date": f"{created_at.day} {MESES[created_at.month - 1]} {created_at.year}",
                "paid": p.is_paid,
                "status": "Pagado" if p.is_paid else "Pendiente",
            }
        )

    weight_history = []
    for i, w in enumerate(weights):
        previous = weights[i + 1].weight if i + 1 < len(weights) else None
        delta = (w.weight - previous) if previous is not None else None
        weight_history.append(
            {
                "id": w.pk,
                "date": _fecha(timezone.localtime(w.created).date()),
                "weight": f"{w.weight} kg",
                "delta": f"{'+' if delta and delta > 0 else ''}{delta} kg" if delta else None,
                "up": bool(delta and delta > 0),
            }
        )

    devices = [
        {
            "id": d.pk,
            "platform": d.get_platform_display(),
            "deviceId": d.device_id[:18],
            "active": d.is_active,
            "seen": _fecha(timezone.localtime(d.modified).date()),
        }
        for d in Device.objects.filter(user=user).order_by("-modified")[:5]
    ]

    birthdate = profile.birthdate if profile else None
    age = None
    if birthdate:
        age = today.year - birthdate.year - (
            (today.month, today.day) < (birthdate.month, birthdate.day)
        )

    return {
        "member": {
            "id": user.pk,
            "name": display_name(user) or "Sin nombre",
            "initials": initials(user),
            "photo": photo_url(user),
            "email": user.email,
            "phone": user.phone_number or "—",
            "verified": user.is_verified,
            "joined": _fecha(timezone.localtime(user.date_joined).date()),
            "status": state,
            "tone": tone,
        },
        "kpis": [
            _kpi("workouts", "dumbbell", "Entrenamientos", total_entrenos, None, ""),
            _kpi(
                "racha",
                "flame",
                "Racha actual",
                f"{streak.weeks} semanas" if streak else "Sin racha",
                None,
                "",
            ),
            _kpi(
                "ranking",
                "trophy",
                "Puesto en ranking",
                f"#{ranking.position}" if ranking else "Sin puesto",
                None,
                "",
            ),
            _kpi(
                "peso",
                "scale",
                "Peso actual",
                f"{current_weight} kg" if current_weight else "Sin registro",
                None,
                "",
            ),
        ],
        # What the form edits. Values go in the shape an <input> expects,
        # not formatted: date wants ISO and number wants a number.
        "form": {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number or "",
            "birthdate": birthdate.isoformat() if birthdate else "",
            "height": profile.height if profile and profile.height else "",
            "profession": (profile.profession if profile else "") or "",
            "instagram": (profile.instagram if profile else "") or "",
            "address": (profile.address if profile else "") or "",
            "emergency_contact": (profile.emergency_contact if profile else "") or "",
            "emergency_contact_phone": (
                profile.emergency_contact_phone if profile else ""
            ) or "",
            "hide_from_leaderboard": bool(profile and profile.hide_from_leaderboard),
        },
        "age": f"{age} años" if age is not None else None,
        "membership": {
            "plan": membership.plan.name if membership and membership.plan else None,
            "type": membership.get_membership_type_display() if membership else None,
            "price": (
                f"$ {_money(membership.plan.price):,}".replace(",", ".")
                if membership and membership.plan
                else None
            ),
            "duration": f"{duration} días" if duration else None,
            "start": _fecha(membership.init_date) if membership else None,
            "end": _fecha(expires),
            "daysLeft": days_left,
            "elapsed": elapsed,
            "total": duration,
            "status": state,
            "tone": tone,
            "isTicketPack": bool(membership and membership.sessions_total),
            "sessionsTotal": membership.sessions_total if membership else 0,
            "sessionsUsed": membership.sessions_used if membership else 0,
            "sessionsLeft": membership.sessions_left if membership else None,
        },
        "weekly": weekly,
        "weeklyTotal": sum(w["value"] for w in weekly),
        "activity": activity,
        "payments": payments,
        "weights": weight_history,
        "devices": devices,
    }


def class_detail(class_id, today, days=30):
    """«42. Class - Detail 360»: everything that happens in one schedule."""
    klass = Classes.objects.select_related("training_type").get(pk=class_id)
    since = today - timedelta(days=days)
    kind = klass.training_type

    start = klass.hour_init.hour * 60 + klass.hour_init.minute
    end = klass.hour_end.hour * 60 + klass.hour_end.minute
    minutes = end - start

    slots = Slot.objects.filter(class_training=klass)
    window = slots.filter(date__gte=since, date__lte=today)
    window_bookings = UserTraining.objects.filter(slot__in=window)
    confirmadas = window_bookings.filter(ACTIVAS).count()
    cancelled = window_bookings.filter(
        status=UserTraining.Status.CANCELLED
    ).count()
    window_places = window.aggregate(t=Sum("max_places"))["t"] or 0
    window_sessions = window.count()
    occupancy = round((confirmadas / window_places) * 100) if window_places else None

    def _sesiones(queryset, limite):
        rows = []
        for slot in queryset.annotate(
            taken=Count(
                "user_trainings",
                filter=~Q(user_trainings__status=UserTraining.Status.CANCELLED),
                distinct=True,
            )
        )[:limite]:
            pct = round((slot.taken / slot.max_places) * 100) if slot.max_places else 0
            if slot.taken == 0:
                label, tone = "Sin reservas", "neutral"
            elif pct >= 100:
                label, tone = "Llena", "error"
            elif pct >= 85:
                label, tone = "Casi llena", "warning"
            else:
                label, tone = "Con cupo", "success"
            rows.append(
                {
                    "id": slot.pk,
                    "date": _fecha(slot.date),
                    "taken": slot.taken,
                    "places": slot.max_places,
                    "occupancy": pct,
                    "status": label,
                    "tone": tone,
                }
            )
        return rows

    upcoming = _sesiones(slots.filter(date__gte=today).order_by("date"), 5)

    next_slot = slots.filter(date__gte=today).order_by("date").first()
    enrolled = []
    if next_slot:
        for r in (
            UserTraining.objects.filter(slot=next_slot)
            .select_related("user", "user__profile")
            .prefetch_related("user__memberships__plan")
            .order_by("created")
        ):
            activa = next((m for m in r.user.memberships.all() if m.is_active), None)
            cancelada = r.status == UserTraining.Status.CANCELLED
            enrolled.append(
                {
                    "id": r.pk,
                    "userId": r.user_id,
                    "name": display_name(r.user) or "Sin nombre",
                    "initials": initials(r.user),
                    "photo": photo_url(r.user),
                    "email": r.user.email,
                    "plan": activa.plan.name if activa and activa.plan else "Sin membresía",
                    "booked": _fecha(timezone.localtime(r.created).date()),
                    "status": "Cancelada" if cancelada else "Confirmada",
                    "tone": "error" if cancelada else "success",
                }
            )

    weeks = _iso_weeks(today, 12)
    by_week = []
    for year, week, lunes in weeks:
        domingo = lunes + timedelta(days=6)
        de_la_semana = slots.filter(date__gte=lunes, date__lte=domingo)
        places = de_la_semana.aggregate(t=Sum("max_places"))["t"] or 0
        taken = (
            UserTraining.objects.filter(slot__in=de_la_semana).filter(ACTIVAS).count()
        )
        by_week.append(
            {
                "label": str(week),
                "value": round((taken / places) * 100) if places else 0,
            }
        )

    counts = list(
        UserTraining.objects.filter(slot__class_training=klass)
        .filter(ACTIVAS)
        .values("user_id")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )
    # values() knows nothing about the photo: users are fetched whole in one
    # extra query and reordered by the count.
    by_id = {
        u.pk: u
        for u in User.objects.filter(
            pk__in=[c["user_id"] for c in counts]
        ).select_related("profile")
    }
    frequent = []
    for row in counts:
        user_frec = by_id.get(row["user_id"])
        if not user_frec:
            continue
        frequent.append(
            {
                "id": user_frec.pk,
                "name": display_name(user_frec) or "Sin nombre",
                "initials": initials(user_frec),
                "photo": photo_url(user_frec),
                "count": row["total"],
            }
        )

    first = slots.order_by("date").first()
    delivered_count = slots.filter(date__lte=today).count()
    attendances = (
        UserTraining.objects.filter(slot__date__lte=today, slot__class_training=klass)
        .filter(ACTIVAS)
        .count()
    )
    todas = UserTraining.objects.filter(slot__class_training=klass).count()
    cancelled_total = UserTraining.objects.filter(
        slot__class_training=klass, status=UserTraining.Status.CANCELLED
    ).count()
    best = max(by_week, key=lambda w: w["value"], default=None)

    return {
        "klass": {
            "id": klass.pk,
            "typeId": kind.pk,
            "name": kind.name,
            "kind": "Clase grupal" if kind.is_group else "Entrenamiento individual",
            "day": klass.get_day_display(),
            "time": f"{_hora(klass.hour_init)} – {_hora(klass.hour_end)}",
            "duration": f"{minutes} min" if minutes > 0 else "—",
            "places": next_slot.max_places if next_slot else None,
            "photo": class_photo(kind),
        },
        "kpis": [
            _kpi("bookings", "calendar-check", f"Reservas ({days} días)", confirmadas, None, ""),
            _kpi(
                "ocupacion",
                "flame",
                "Ocupación promedio",
                f"{occupancy}%" if occupancy is not None else "Sin sesiones",
                None,
                "",
            ),
            _kpi("sessions", "repeat", f"Sesiones ({days} días)", window_sessions, None, ""),
            _kpi("cancelled", "circle-x", "Cancelaciones", cancelled, None, ""),
        ],
        "form": {
            "name": kind.name,
            "is_group": kind.is_group,
            "day": klass.day,
            "hour_init": klass.hour_init.strftime("%H:%M"),
            "hour_end": klass.hour_end.strftime("%H:%M"),
            "photo": class_photo(kind),
            "hasPhoto": bool(kind.photo),
        },
        "dayChoices": [{"value": value, "label": label} for value, label in Classes.DaysChoices.choices],
        "sessions": upcoming,
        "nextDate": _fecha(next_slot.date) if next_slot else None,
        "enrolled": enrolled,
        "weekly": by_week,
        "weeklyAverage": (
            round(sum(w["value"] for w in by_week) / len(by_week))
            if by_week
            else 0
        ),
        "frequent": frequent,
        "history": [
            ["Primera sesión", _fecha(first.date) if first else "—"],
            ["Sesiones dictadas", str(delivered_count)],
            [
                "Asistencia media",
                f"{round(attendances / delivered_count, 1)} usuarios" if delivered_count else "—",
            ],
            [
                "Mejor semana",
                f"Semana {best['label']} · {best['value']}%" if best else "—",
            ],
            [
                "Tasa de cancelación",
                f"{round((cancelled_total / todas) * 100, 1)}%" if todas else "—",
            ],
        ],
    }


def notifications_page(today, days=30):
    """The KPIs for «11. Notifications».

    The table does not come from here: there are tens of thousands of rows and they
    are paginated on the server (NotificationFeedView). This is only the header."""
    since = today - timedelta(days=days)
    del_periodo = PushNotification.objects.filter(created__date__gte=since)

    sent_today = PushNotification.objects.filter(created__date=today).count()
    yesterday = PushNotification.objects.filter(
        created__date=today - timedelta(days=1)
    ).count()

    ENTREGADAS = (PushNotification.Status.DELIVERED, PushNotification.Status.READ)
    delivered = del_periodo.filter(status__in=ENTREGADAS).count()
    failed = del_periodo.filter(status=PushNotification.Status.FAILED).count()
    # Pending ones do not count: we do not know yet whether they arrived.
    resolved = del_periodo.exclude(
        status=PushNotification.Status.PENDING
    ).count()

    return {
        "kpis": [
            _kpi(
                "hoy",
                "bell",
                "Enviadas hoy",
                sent_today,
                pct_change(sent_today, yesterday),
                "frente a ayer",
            ),
            _kpi("delivered", "badge-check", f"Entregadas ({days} días)", delivered, None, ""),
            _kpi("failed", "circle-x", f"Fallidas ({days} días)", failed, None, ""),
            _kpi(
                "tasa",
                "percent",
                "Tasa de entrega",
                f"{round((delivered / resolved) * 100)}%" if resolved else "—",
                None,
                "",
            ),
        ],
    }


def notification_detail(notification_id):
    """One delivery in detail: the notification and a log per device.

    It is the only thing that explains why it failed: `error_message` comes from
    Expo's ticket and the payloads are the request and response exactly as sent."""
    notification = (
        PushNotification.objects.select_related("user")
        .prefetch_related("logs__device")
        .get(pk=notification_id)
    )

    def _momento(value):
        if not value:
            return None
        local = timezone.localtime(value)
        return f"{local.day} {MESES[local.month - 1]} {local.year}, {local:%H:%M}"

    logs = []
    for log in notification.logs.all().order_by("created"):
        logs.append(
            {
                "id": log.pk,
                "device": log.device.get_platform_display() if log.device else "Dispositivo borrado",
                "deviceId": log.device.device_id[:18] if log.device else None,
                "deviceActive": log.device.is_active if log.device else None,
                # The full token identifies the device: only the tail is shown,
                # enough to tell devices apart without leaving it copyable.
                "token": f"…{log.expo_push_token[-12:]}" if log.expo_push_token else "—",
                "ok": log.status == PushNotificationLog.Status.SUCCESS,
                "status": log.get_status_display(),
                "error": log.error_message or None,
                "receipt": log.expo_receipt_id or None,
                "at": _momento(log.created),
                "request": log.request_payload,
                "response": log.response_payload,
            }
        )

    failures = [entry for entry in logs if not entry["ok"]]
    return {
        "id": notification.pk,
        "userId": notification.user_id,
        "userName": display_name(notification.user) or "Sin nombre",
        "userInitials": initials(notification.user),
        "userPhoto": photo_url(notification.user),
        "userEmail": notification.user.email,
        "title": notification.title,
        "body": notification.body,
        "type": notification.get_notification_type_display(),
        "status": notification.status,
        "statusLabel": notification.get_status_display(),
        "created": _momento(notification.created),
        "sentAt": _momento(notification.sent_at),
        "readAt": _momento(notification.read_at),
        "scheduledFor": _momento(notification.scheduled_for),
        "data": notification.data,
        "logs": logs,
        "attempts": len(logs),
        "failures": len(failures),
        # The summary at the top of the modal: why it failed, in one line.
        "summary": (
            failures[0]["error"]
            if failures and failures[0]["error"]
            else "Sin intentos de envío registrados"
            if not logs
            else None
        ),
    }


# ---------------------------------------------------------------------------
# Videos: biblioteca, packages y a quien le llegan.
# ---------------------------------------------------------------------------


def _duracion(seconds):
    if not seconds:
        return "—"
    minutes, rest = divmod(int(seconds), 60)
    return f"{minutes}:{rest:02d} min"


def _video_row(video):
    return {
        "id": video.pk,
        "name": video.name,
        "description": video.description,
        "source": video.source,
        "sourceLabel": video.get_source_display(),
        "poster": video.poster,
        "playback": video.playback,
        "posterSecond": video.poster_second,
        "duration": _duracion(video.duration_seconds),
        "seconds": video.duration_seconds,
        "level": video.get_level_display(),
        "levelValue": video.level,
        "type": video.training_type.name if video.training_type else None,
        "typeId": video.training_type_id,
        "published": video.is_published,
    }


def videos_page(today):
    """The video library."""
    queryset = Video.objects.select_related("training_type").annotate(
        en_paquetes=Count("items", distinct=True),
        views=Count("progress", distinct=True),
    )

    rows = []
    for i, video in enumerate(queryset, start=1):
        rows.append(
            {
                **_video_row(video),
                "no": i,
                "packages": video.en_paquetes,
                "views": video.views,
            }
        )

    publicados = sum(1 for f in rows if f["published"])
    minutes = sum(f["seconds"] for f in rows) // 60
    sin_fuente = sum(1 for f in rows if not f["playback"])

    return {
        "kpis": [
            _kpi("total", "video", "Videos en biblioteca", len(rows), None, ""),
            _kpi("published", "badge-check", "Publicados", publicados, None, ""),
            _kpi("minutes", "clock", "Minutos de contenido", minutes, None, ""),
            _kpi("orphans", "circle-x", "Sin fuente cargada", sin_fuente, None, ""),
        ],
        "rows": rows,
    }


def _alcance(package, total_users):
    """How many people a package reaches, counting nobody twice."""
    reached = set()
    labels = []
    for a in package.assignments.all():
        if a.everyone:
            return total_users, ["Todos los usuarios"]
        if a.user_id:
            reached.add(a.user_id)
            labels.append(display_name(a.user) or a.user.email)
        elif a.plan_id:
            ids = UserMembership.objects.filter(
                is_active=True, plan_id=a.plan_id
            ).values_list("user_id", flat=True)
            reached.update(ids)
            labels.append(f"Plan {a.plan.name}")
    return len(reached), labels


def packages_page(today):
    """The video packages."""
    total_users = client_users().count()
    queryset = (
        VideoPackage.objects.prefetch_related(
            "assignments__user", "assignments__plan", "items"
        ).annotate(n_videos=Count("items", distinct=True))
    )

    rows = []
    for i, package in enumerate(queryset, start=1):
        reach, labels = _alcance(package, total_users)
        rows.append(
            {
                "no": i,
                "id": package.pk,
                "name": package.name,
                "description": package.description,
                "cover": package.cover.url if package.cover else None,
                "kind": package.get_kind_display(),
                "kindValue": package.kind,
                "videos": package.n_videos,
                "reach": reach,
                "targets": labels,
                "published": package.is_published,
            }
        )

    individuales = sum(1 for f in rows if f["kindValue"] == "individual")
    return {
        "kpis": [
            _kpi("total", "layers", "Paquetes", len(rows), None, ""),
            _kpi(
                "publicados",
                "badge-check",
                "Publicados",
                sum(1 for f in rows if f["published"]),
                None,
                "",
            ),
            _kpi("individual", "user-plus", "Individuales", individuales, None, ""),
            _kpi(
                "sinvideos",
                "circle-x",
                "Sin videos",
                sum(1 for f in rows if f["videos"] == 0),
                None,
                "",
            ),
        ],
        "rows": rows,
    }


def package_detail(package_id):
    """A package builder: its videos in order and who receives it."""
    package = (
        VideoPackage.objects.prefetch_related(
            "items__video__training_type", "assignments__user", "assignments__plan"
        ).get(pk=package_id)
    )
    total_users = client_users().count()
    reach, _ = _alcance(package, total_users)

    items = []
    inside = set()
    for item in package.items.all():
        inside.add(item.video_id)
        items.append(
            {
                "id": item.pk,
                "videoId": item.video_id,
                "order": item.order,
                "notes": item.notes,
                **_video_row(item.video),
            }
        )

    assignments = []
    for a in package.assignments.all():
        if a.everyone:
            label, sub, kind = "Todos los usuarios", f"{total_users} usuarios", "everyone"
        elif a.user_id:
            label = display_name(a.user) or a.user.email
            sub, kind = a.user.email, "user"
        else:
            activos = UserMembership.objects.filter(
                is_active=True, plan_id=a.plan_id
            ).count()
            label, sub, kind = f"Plan {a.plan.name}", f"{activos} con membresía activa", "plan"
        assignments.append(
            {"id": a.pk, "label": label, "sub": sub, "kind": kind,
             "userId": a.user_id, "initials": initials(a.user) if a.user_id else None}
        )

    # What can be added: published and not already inside.
    available = [
        {"id": v.pk, "name": v.name, "duration": _duracion(v.duration_seconds),
         "source": v.get_source_display(), "poster": v.poster}
        for v in Video.objects.select_related("training_type")
        .filter(is_published=True)
        .exclude(pk__in=inside)
        .order_by("name")
    ]

    drafts = Video.objects.filter(is_published=False).exclude(pk__in=inside).count()
    seconds = sum(i["seconds"] for i in items)
    views = VideoProgress.objects.filter(video_id__in=inside)
    completados = views.filter(completed_at__isnull=False).count()

    return {
        "package": {
            "id": package.pk,
            "name": package.name,
            "description": package.description,
            "cover": package.cover.url if package.cover else None,
            "kind": package.kind,
            "kindLabel": package.get_kind_display(),
            "published": package.is_published,
        },
        "kpis": [
            _kpi("videos", "video", "Videos", len(items), None, ""),
            _kpi("duration", "clock", "Duración total", _duracion(seconds), None, ""),
            _kpi("reach", "users", "Usuarios alcanzados", reach, None, ""),
            _kpi("completed", "badge-check", "Videos completados", completados, None, ""),
        ],
        "items": items,
        "progress": package_progress(package_id),
        "assignments": assignments,
        "available": available,
        "drafts": drafts,
        "kindChoices": [{"value": value, "label": label} for value, label in VideoPackage.Kind.choices],
        "plans": [
            {"value": str(p.pk), "label": p.name}
            for p in NeuralPlan.objects.order_by("duration")
        ],
        # The whole list ships in the props: ~740 users, about 70 KB, so the
        # search answers without hitting the server on every keystroke.
        "users": [
            {
                "id": u.pk,
                "name": display_name(u) or u.email,
                "email": u.email,
                "initials": initials(u),
                "photo": photo_url(u),
            }
            for u in assignable_users()
            .select_related("profile")
            .order_by("first_name", "last_name")
        ],
    }


def _momento_corto(value):
    if not value:
        return None
    local = timezone.localtime(value)
    return f"{local.day} {MESES[local.month - 1]}"


def member_videos(user):
    """The packages a member receives and how much of each one they watched.

    A package can reach them three ways --directly, through their plan, or by
    being for everyone-- and must not appear twice if two of them apply.

    It goes down video by video: the team does not want to know only that
    something was assigned, it wants to know whether it is being watched."""
    plans = UserMembership.objects.filter(
        user=user, is_active=True
    ).values_list("plan_id", flat=True)

    assigned = (
        VideoPackage.objects.filter(
            Q(assignments__user=user)
            | Q(assignments__plan_id__in=list(plans))
            | Q(assignments__everyone=True),
            is_published=True,
        )
        .distinct()
        .prefetch_related("items__video")
    )

    progress = {
        p.video_id: p
        for p in VideoProgress.objects.filter(user=user)
    }

    rows = []
    for package in assigned:
        videos = [item.video for item in package.items.all()]
        detail = []
        segundos_vistos = 0
        segundos_totales = 0
        for video in videos:
            p = progress.get(video.pk)
            seen = p.seconds if p else 0
            segundos_vistos += min(seen, video.duration_seconds or seen)
            segundos_totales += video.duration_seconds
            detail.append(
                {
                    "id": video.pk,
                    "name": video.name,
                    "poster": video.poster,
                    "duration": _duracion(video.duration_seconds),
                    "watched": _duracion(seen) if seen else None,
                    "percent": p.percent if p else 0,
                    "completed": bool(p and p.completed_at),
                    "lastSeen": _momento_corto(p.modified) if p else None,
                }
            )

        completed_count = sum(1 for d in detail if d["completed"])
        rows.append(
            {
                "id": package.pk,
                "name": package.name,
                "cover": package.cover.url if package.cover else None,
                "kind": package.get_kind_display(),
                "videos": len(videos),
                "done": completed_count,
                # The percentage is of time watched, not of finished videos:
                # somebody halfway through every video is not at 0%.
                "percent": (
                    round((segundos_vistos / segundos_totales) * 100)
                    if segundos_totales
                    else 0
                ),
                "items": detail,
            }
        )
    return rows


def package_progress(package_id):
    """Who watched what inside a package.

    Two readings: per video --which one gets abandoned-- and per member --who is
    falling behind. Both come from the same set of VideoProgress rows."""
    package = VideoPackage.objects.prefetch_related("items__video").get(pk=package_id)
    videos = [item.video for item in package.items.all()]
    if not videos:
        return {"videos": [], "members": [], "started": 0, "finished": 0}

    ids = [v.pk for v in videos]
    rows = list(
        VideoProgress.objects.filter(video_id__in=ids)
        .select_related("user", "user__profile", "video")
    )

    by_video = {v.pk: [] for v in videos}
    by_user = {}
    for row in rows:
        by_video[row.video_id].append(row)
        by_user.setdefault(row.user_id, []).append(row)

    video_rows = []
    for video in videos:
        views = by_video[video.pk]
        completed_count = sum(1 for f in views if f.completed_at)
        average = (
            round(sum(f.percent for f in views) / len(views)) if views else 0
        )
        video_rows.append(
            {
                "id": video.pk,
                "name": video.name,
                "poster": video.poster,
                "duration": _duracion(video.duration_seconds),
                "viewers": len(views),
                "completed": completed_count,
                "average": average,
            }
        )

    user_rows = []
    for user_id, theirs in by_user.items():
        user = theirs[0].user
        completed_count = sum(1 for f in theirs if f.completed_at)
        seen = sum(min(f.seconds, f.video.duration_seconds or f.seconds) for f in theirs)
        totales = sum(v.duration_seconds for v in videos)
        user_rows.append(
            {
                "id": user_id,
                "name": display_name(user) or user.email,
                "initials": initials(user),
                "photo": photo_url(user),
                "done": completed_count,
                "videos": len(videos),
                "percent": round((seen / totales) * 100) if totales else 0,
                "lastSeen": _momento_corto(max(f.modified for f in theirs)),
            }
        )
    user_rows.sort(key=lambda u: -u["percent"])

    return {
        "videos": video_rows,
        "members": user_rows[:20],
        "started": len(by_user),
        "finished": sum(1 for u in user_rows if u["done"] == len(videos)),
    }
