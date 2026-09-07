"""Recuperación de contraseña con código de 6 dígitos.

La app no tiene deep links, así que el link por correo dejaba al usuario en el
navegador sin forma de volver. Con un código se resuelve dentro de la app.

Un código de 6 dígitos son un millón de combinaciones, pero lo que lo hace
seguro no es el largo: es que se quema a los 5 intentos, vive 10 minutos y
pedir uno nuevo mata al anterior.
"""

import hashlib
import secrets

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from neural.users.models import PasswordResetCode, User

# Cuántas veces se puede pedir un código antes de que sirva para inundar una
# casilla ajena.
MAX_REQUESTS_PER_EMAIL = 3
MAX_REQUESTS_PER_IP = 10
REQUEST_WINDOW = 60 * 60


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _rate_limited(request, email):
    """True si hay que frenar. Cuenta por correo y por IP por separado."""
    checks = (
        (f"pwreset:email:{email.lower()}", MAX_REQUESTS_PER_EMAIL),
        (f"pwreset:ip:{_client_ip(request)}", MAX_REQUESTS_PER_IP),
    )
    for key, limit in checks:
        used = cache.get(key, 0)
        if used >= limit:
            return True
        cache.set(key, used + 1, REQUEST_WINDOW)
    return False


def _hash_token(token):
    """El token tiene entropía de sobra, así que alcanza un hash directo.

    Además permite buscarlo en la base, cosa que un hash salado no permite.
    """
    return hashlib.sha256(token.encode()).hexdigest()


def _send_code(user, code):
    context = {"code": code, "user": user, "minutes": 10}
    subject = "Tu código para recuperar la contraseña de Neural"
    body = render_to_string("registration/password_reset_code.txt", context)
    html = render_to_string("registration/password_reset_code.html", context)
    message = EmailMultiAlternatives(
        subject, body, settings.DEFAULT_FROM_EMAIL, [user.email]
    )
    message.attach_alternative(html, "text/html")
    message.send(fail_silently=True)


class PasswordResetRequestView(APIView):
    """Manda un código de 6 dígitos al correo."""

    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip()
        if not email:
            return Response(
                {"detail": "Email es requerido"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not _rate_limited(request, email):
            user = User.objects.filter(email__iexact=email, is_active=True).first()
            if user:
                # Pedir uno nuevo invalida el anterior: si no, quedan dos vivos
                # y el usuario prueba el viejo.
                user.reset_codes.filter(used_at__isnull=True).update(
                    used_at=timezone.now()
                )
                code = f"{secrets.randbelow(1000000):06d}"
                PasswordResetCode.objects.create(
                    user=user,
                    code_hash=make_password(code),
                    expires_at=timezone.now() + PasswordResetCode.CODE_TTL,
                )
                _send_code(user, code)

        # Respuesta siempre igual: si no, sirve para averiguar quién tiene
        # cuenta. Tampoco cambia cuando frenamos por rate limit.
        return Response(
            {"message": "Si el correo está registrado, te enviamos un código"}
        )


class PasswordResetVerifyView(APIView):
    """Cambia el código por un token de un solo uso."""

    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip()
        code = (request.data.get("code") or "").strip()
        if not email or not code:
            return Response(
                {"detail": "Email y código son requeridos"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invalid = Response(
            {"detail": "El código no es válido"}, status=status.HTTP_400_BAD_REQUEST
        )

        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if not user:
            return invalid

        entry = user.reset_codes.filter(used_at__isnull=True).first()
        if not entry:
            return invalid
        if entry.is_expired:
            return Response(
                {"detail": "El código venció. Pedí uno nuevo."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if entry.is_burned:
            return Response(
                {"detail": "Demasiados intentos. Pedí un código nuevo."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not check_password(code, entry.code_hash):
            entry.attempts += 1
            entry.save(update_fields=["attempts", "modified"])
            restantes = PasswordResetCode.MAX_ATTEMPTS - entry.attempts
            if restantes <= 0:
                return Response(
                    {"detail": "Demasiados intentos. Pedí un código nuevo."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"detail": "El código no es correcto", "attempts_left": restantes},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = secrets.token_urlsafe(32)
        entry.token_hash = _hash_token(token)
        entry.token_expires_at = timezone.now() + PasswordResetCode.TOKEN_TTL
        entry.save(update_fields=["token_hash", "token_expires_at", "modified"])
        return Response({"reset_token": token})


class PasswordResetConfirmView(APIView):
    """Cambia la contraseña con el token que devolvió verify."""

    permission_classes = [AllowAny]

    def post(self, request):
        token = (request.data.get("reset_token") or "").strip()
        new_password = request.data.get("new_password") or ""
        if not token or not new_password:
            return Response(
                {"detail": "Token y contraseña son requeridos"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        entry = PasswordResetCode.objects.filter(
            token_hash=_hash_token(token), used_at__isnull=True
        ).first()
        if not entry or not entry.token_expires_at:
            return Response(
                {"detail": "El enlace no es válido o ya se usó"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if timezone.now() >= entry.token_expires_at:
            return Response(
                {"detail": "La sesión venció. Pedí un código nuevo."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password, entry.user)
        except ValidationError as exc:
            return Response(
                {"detail": "La contraseña no cumple los requisitos",
                 "errors": list(exc.messages)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = entry.user
        user.set_password(new_password)
        user.save(update_fields=["password"])

        # El token muere acá, y de paso cualquier otro código vivo del usuario.
        now = timezone.now()
        entry.used_at = now
        entry.save(update_fields=["used_at", "modified"])
        user.reset_codes.filter(used_at__isnull=True).update(used_at=now)

        return Response({"message": "Contraseña actualizada"})
