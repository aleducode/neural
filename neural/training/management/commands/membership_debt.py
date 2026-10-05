"""Quién está reservando sin membresía vigente.

Es la lista que recepción necesita antes de encender
ENFORCE_MEMBERSHIP_ON_BOOKING: encenderlo sin regularizar a esta gente los deja
sin entrenar de un día para otro.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from neural.training.rules import enforced, memberships_in_debt
from neural.users.display import display_name


class Command(BaseCommand):
    help = "Lista quién reserva sin membresía vigente."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Cuántos días hacia atrás mirar (por defecto 30).",
        )
        parser.add_argument(
            "--csv",
            action="store_true",
            help="Salida separada por comas, para pasarla a una hoja de cálculo.",
        )

    def handle(self, *args, **options):
        until = timezone.localdate()
        since = until - timedelta(days=options["days"])
        filas = memberships_in_debt(since, until)

        if options["csv"]:
            self.stdout.write("nombre,email,telefono,reservas,ultima,motivo")
            for f in filas:
                u = f["user"]
                self.stdout.write(
                    f'"{display_name(u)}",{u.email},{u.phone_number or ""},'
                    f'{f["reservas"]},{f["ultima"]},"{f["motivo"]}"'
                )
            return

        estado = "ENCENDIDO" if enforced() else "apagado"
        self.stdout.write(f"\nControl de membresía al reservar: {estado}")
        self.stdout.write(f"Período: {since} a {until}\n")

        if not filas:
            self.stdout.write(self.style.SUCCESS("Nadie reservó sin membresía."))
            return

        total = sum(f["reservas"] for f in filas)
        self.stdout.write(
            self.style.WARNING(
                f"{len(filas)} personas, {total} reservas sin membresía vigente.\n"
            )
        )
        self.stdout.write(f"{'nombre':<28}{'email':<34}{'res':>4}  última      motivo")
        self.stdout.write("-" * 110)
        for f in filas:
            u = f["user"]
            self.stdout.write(
                f"{display_name(u)[:27]:<28}{u.email[:33]:<34}"
                f'{f["reservas"]:>4}  {f["ultima"]}  {f["motivo"][:40]}'
            )

        self.stdout.write(
            "\nRegularizalas antes de poner ENFORCE_MEMBERSHIP_ON_BOOKING=True.\n"
        )
