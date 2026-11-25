"""Member accounts: creating them and the emails that come with them.

The app's sign-up and the team panel both create members, so the parts they
share live here instead of in either view.
"""

import logging

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from neural.users.models import Profile, User

logger = logging.getLogger(__name__)


def unique_username(email):
    """A free username built from the email's local part.

    The login uses the email; username is still required and unique on
    AbstractUser, so it only has to not collide."""
    base = email.split("@")[0]
    username = base
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base}{counter}"
        counter += 1
    return username


def create_member(*, email, first_name, last_name, phone_number=None, birthdate=None):
    """A member account opened by the team.

    It starts verified --the team is vouching for the person-- and with no
    usable password: the member picks one from the welcome email, so nobody at
    reception ever knows it."""
    user = User(
        email=email,
        username=unique_username(email),
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        is_verified=True,
        is_client=True,
    )
    user.set_unusable_password()
    user.save()
    if birthdate:
        Profile.objects.update_or_create(user=user, defaults={"birthdate": birthdate})
    return user


def password_link(request, user):
    """The one-time link to set a password, on the web reset screen."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    path = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
    return request.build_absolute_uri(path)


def send_password_email(request, user, *, welcome):
    """Email the member a link to choose their password.

    `welcome` changes only the wording: a new account and a reset sent by the
    team are the same link. Returns whether the email went out."""
    context = {
        "user": user,
        "link": password_link(request, user),
        "welcome": welcome,
        "days": settings.PASSWORD_RESET_TIMEOUT // 86400,
    }
    subject = (
        "Tu cuenta de Neural está lista: elegí tu contraseña"
        if welcome
        else "Elegí una contraseña nueva para Neural"
    )
    body = render_to_string("registration/account_password_email.txt", context)
    html = render_to_string("registration/account_password_email.html", context)
    message = EmailMultiAlternatives(
        subject, body, settings.DEFAULT_FROM_EMAIL, [user.email]
    )
    message.attach_alternative(html, "text/html")
    try:
        message.send()
    except Exception:
        logger.exception("Could not send the password email to user %s", user.pk)
        return False
    return True
