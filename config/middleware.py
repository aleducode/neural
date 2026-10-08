"""Middleware to ensure active membership."""

# Django
from django.shortcuts import redirect
from django.urls import reverse


class MembershipMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Code to be executed for each request before the view is called."""
        if not request.user.is_anonymous:
            if not request.user.is_staff:
                user = request.user
                if not user.is_verified or not user.is_client:
                    trusted_domains = [
                        reverse("users:pending"),
                        reverse("users:logout"),
                    ]
                    # Except some urls
                    if request.path not in trusted_domains:
                        return redirect("users:pending")
        response = self.get_response(request)
        return response


class AppOnlyMiddleware:
    """La web de socios dejó de existir: todo va a la app.

    Se hace acá y no incluyendo una plantilla en cada página porque así no se
    escapa ninguna: una pantalla nueva queda cerrada por omisión, sin que nadie
    tenga que acordarse. Y porque bloquea de verdad --el aviso que había antes
    era JavaScript encima de una página que igual cargaba--.

    Lo que sigue abierto, y por qué:
      - El panel del equipo y el admin: es con lo que trabajan.
      - La API: es lo que consume la app.
      - Estáticos y media: los sirve la propia página de descarga.
      - Las páginas de borrado de datos y de cuenta: Google Play y App Store
        exigen que sean públicas y alcanzables desde un navegador.
      - Recuperar la contraseña: el enlace llega por correo y se abre en el
        navegador. Cerrarlo dejaría a alguien sin poder volver a entrar.
    """

    # Prefijos fijos.
    ABIERTAS = (
        "/manager/",
        "/api/",
        "/static/",
        "/media/",
        "/password_reset/",
        "/reset/",
    )

    # Las de cumplimiento se resuelven por nombre y no a mano: escribí
    # "/account-deletion" de memoria y la ruta real es "/delete/", así que la
    # página quedó bloqueada sin que se notara. Con el nombre, si alguien
    # cambia la ruta la exención lo sigue.
    POR_NOMBRE = (
        "users:account_deletion_info",
        "users:account_deletion",
        "users:data_deletion_info",
        "users:data_deletion",
    )

    def __init__(self, get_response):
        self.get_response = get_response
        from django.conf import settings
        from django.urls import NoReverseMatch, reverse

        # ADMIN_URL viene de settings y no es fija: en producción es otra.
        self.admin_url = "/" + str(settings.ADMIN_URL).lstrip("/")

        abiertas = list(self.ABIERTAS)
        for nombre in self.POR_NOMBRE:
            try:
                abiertas.append(reverse(nombre))
            except NoReverseMatch:
                # Si la ruta ya no existe, no hay nada que dejar abierto.
                pass
        self.abiertas = tuple(abiertas)

    def abierta(self, path):
        if path.startswith(self.admin_url):
            return True
        return any(path.startswith(p) for p in self.abiertas)

    def __call__(self, request):
        if self.abierta(request.path):
            return self.get_response(request)

        from django.shortcuts import render

        # 200 y no 403: no es un error del visitante, es que la web se mudó a
        # la app. Un 403 además lo indexarían mal los buscadores.
        return render(request, "shared/get_the_app.html")
