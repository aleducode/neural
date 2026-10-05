"""Check that Cloudflare Stream is wired up correctly.

Run this right after pasting the token: it tells you whether the credential
works, what the account looks like, and whether a direct upload can be opened
--without uploading anything.

Nothing here prints the token. It reports only its presence and length.
"""

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from neural.services import cloudflare_stream as cf


class Command(BaseCommand):
    help = "Verifies the Cloudflare Stream configuration end to end."

    def _ok(self, text):
        self.stdout.write(self.style.SUCCESS(f"  OK    {text}"))

    def _bad(self, text):
        self.stdout.write(self.style.ERROR(f"  FALLA {text}"))

    def _info(self, text):
        self.stdout.write(f"        {text}")

    def handle(self, *args, **options):
        self.stdout.write("\nConfiguración")
        account = settings.CLOUDFLARE_ACCOUNT_ID
        token = settings.CLOUDFLARE_STREAM_TOKEN
        subdomain = settings.CLOUDFLARE_STREAM_SUBDOMAIN

        self._ok(f"Account id: {account}") if account else self._bad("Falta CLOUDFLARE_ACCOUNT_ID")
        self._ok(f"Subdominio: {subdomain}") if subdomain else self._bad(
            "Falta CLOUDFLARE_STREAM_SUBDOMAIN"
        )
        if token:
            # Never print the credential, only enough to tell it apart.
            self._ok(f"Token presente ({len(token)} caracteres)")
        else:
            self._bad("Falta CLOUDFLARE_STREAM_TOKEN")
            self._info("El panel va a subir contra el almacenamiento propio.")
            self._info("Ponelo en .env (NO en .envs/.local/, que se versiona).")
            return

        self.stdout.write("\nCredencial")
        # An account-owned token verifies against the account endpoint; a user
        # token against /user. Trying the account one first and falling back
        # keeps this working whichever kind was created.
        endpoints = [
            f"{cf.API}/accounts/{account}/tokens/verify",
            f"{cf.API}/user/tokens/verify",
        ]
        verified = None
        for url in endpoints:
            try:
                response = requests.get(
                    url,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=cf.TIMEOUT,
                )
            except requests.RequestException as error:
                self._bad(f"No se pudo contactar a Cloudflare: {error}")
                return
            if response.status_code == 200 and response.json().get("success"):
                verified = url
                break

        if verified:
            tipo = "de cuenta" if "/accounts/" in verified else "de usuario"
            self._ok(f"El token es válido y está activo (token {tipo})")
        else:
            self._bad(f"Cloudflare respondió {response.status_code} en los dos endpoints")
            self._info(response.text[:200])
            self._info("Revisá que el token se haya creado y copiado completo.")
            return

        self.stdout.write("\nPermiso sobre Stream")
        try:
            listado = requests.get(
                f"{cf.API}/accounts/{account}/stream",
                headers={"Authorization": f"Bearer {token}"},
                params={"limit": 1},
                timeout=cf.TIMEOUT,
            )
        except requests.RequestException as error:
            self._bad(f"No se pudo leer la biblioteca: {error}")
            return

        if listado.status_code != 200:
            self._bad(f"Lectura rechazada ({listado.status_code})")
            self._info("Al token le falta el permiso Account -> Stream -> Edit.")
            self._info(listado.text[:200])
            return
        self._ok("Lectura permitida")

        propios = cf.list_videos()
        todos = cf.list_videos(creator=None)
        self._info(f"{len(propios)} videos del panel (creator={cf.CREATOR})")
        self._info(f"{len(todos)} videos en toda la cuenta --el resto es de otros productos")

        self.stdout.write("\nSubida directa")
        try:
            upload_url, uid = cf.create_direct_upload("stream-doctor-probe.mp4", 1024)
        except Exception as error:
            self._bad(f"No se pudo abrir una subida: {error}")
            self._info("Al token le falta el permiso de escritura (Stream -> Edit).")
            return

        if upload_url and uid:
            self._ok(f"Subida directa disponible (uid de prueba {uid})")
            # The probe is never written to, but Cloudflare keeps the empty
            # placeholder around; removing it keeps the library clean.
            borrado = requests.delete(
                f"{cf.API}/accounts/{account}/stream/{uid}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=cf.TIMEOUT,
            )
            if borrado.status_code in (200, 204):
                self._ok("Placeholder de prueba borrado")
            else:
                self._info(f"Quedó el placeholder {uid}; borralo a mano si molesta.")
        else:
            self._bad("Cloudflare no devolvió la URL de subida")
            return

        self.stdout.write(self.style.SUCCESS("\nStream está listo para usarse.\n"))
