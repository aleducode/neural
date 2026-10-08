"""Completa la duración de los videos de YouTube que están en cero.

De Cloudflare la duración llega sola; de un enlace de YouTube no hay forma
oficial sin una API key, así que el panel se la pide a quien sube el video. Los
que ya estaban cargados quedaron en cero, y una duración en cero rompe en
silencio el 95% de completado, el tiempo restante y la barra de avance.

Esto la saca de la propia página del video. Es raspado, no una API: puede dejar
de funcionar si YouTube cambia su HTML, y por eso no corre solo al guardar --el
campo del panel sigue siendo la fuente de verdad. Sirve para ponerse al día.
"""

import re

import requests
from django.core.management.base import BaseCommand

from neural.training.models import Video

# Sin un User-Agent de navegador, YouTube devuelve una página sin este dato.
AGENTE = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
PATRON = re.compile(r'"lengthSeconds":"(\d+)"')
TIMEOUT = 20


def duracion_de(youtube_id):
    """Los segundos que dura ese video, o None si no se pudo leer."""
    try:
        respuesta = requests.get(
            f"https://www.youtube.com/watch?v={youtube_id}",
            headers={"User-Agent": AGENTE},
            timeout=TIMEOUT,
        )
    except requests.RequestException:
        return None
    if respuesta.status_code != 200:
        return None
    encontrado = PATRON.search(respuesta.text)
    return int(encontrado.group(1)) if encontrado else None


class Command(BaseCommand):
    help = "Completa la duración de los videos de YouTube que están en cero."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Revisar todos, no sólo los que están en cero.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Decir qué haría, sin guardar nada.",
        )

    def handle(self, *args, **options):
        videos = Video.objects.filter(source=Video.Source.URL)
        if not options["all"]:
            videos = videos.filter(duration_seconds=0)

        candidatos = [v for v in videos if v.youtube_id]
        if not candidatos:
            self.stdout.write(self.style.SUCCESS("No hay nada que completar."))
            return

        self.stdout.write(f"{len(candidatos)} videos de YouTube por revisar\n")
        arreglados = fallados = 0
        for video in candidatos:
            segundos = duracion_de(video.youtube_id)
            nombre = video.name[:40]
            if segundos is None:
                fallados += 1
                self.stdout.write(self.style.ERROR(f"  no se pudo leer  {nombre}"))
                continue
            if segundos == video.duration_seconds:
                self.stdout.write(f"  ya estaba bien   {nombre} ({segundos}s)")
                continue
            if options["dry_run"]:
                self.stdout.write(
                    f"  pondría {segundos:>4}s   {nombre} (hoy {video.duration_seconds}s)"
                )
                continue
            video.duration_seconds = segundos
            video.save(update_fields=["duration_seconds", "modified"])
            arreglados += 1
            self.stdout.write(
                self.style.SUCCESS(f"  {segundos:>4}s           {nombre}")
            )

        self.stdout.write("")
        if options["dry_run"]:
            self.stdout.write("(dry-run: no se guardó nada)")
        else:
            self.stdout.write(self.style.SUCCESS(f"{arreglados} actualizados"))
        if fallados:
            self.stdout.write(
                self.style.WARNING(
                    f"{fallados} sin leer: ponelas a mano desde el panel."
                )
            )
            if fallados == len(candidatos):
                # Comprobado: desde el servidor de produccion fallan los seis,
                # desde una maquina de casa salen los seis. YouTube no le
                # responde igual a una IP de datacenter.
                self.stdout.write(
                    "Fallaron todos. YouTube suele bloquear las IP de "
                    "servidor: corré este comando desde una máquina común."
                )
