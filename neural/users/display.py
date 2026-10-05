"""Cómo se muestra un socio. Una sola regla para toda la aplicación.

Vivía dentro de una vista de la API, y la pantalla de al lado improvisaba la
suya: así fue como el prefijo del correo se publicó dos veces.
"""


def display_name(user):
    """Nombre del socio, o None si nunca lo cargó.

    Nunca cae al prefijo del correo: eso publica media dirección ajena en la
    pantalla de otro. Quien consume esto pinta las iniciales cuando viene
    vacío.
    """
    return user.get_full_name().strip() or None


def initials(user):
    """Dos letras para el avatar. Sin nombre cargado salen del correo.

    Dos letras no reconstruyen una dirección, y son estables para esa persona,
    así que el socio se ve igual en todas las pantallas.
    """
    name = user.get_full_name().strip()
    parts = name.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    if name:
        return name[:2].upper()
    return user.email[:2].upper()


def photo_url(user):
    """La foto del socio, o None.

    Hay dos campos: User.photo y Profile.photo. Gana la del perfil, que es la
    que la app movil deja cambiar; si no hay ninguna, el avatar cae a iniciales.
    """
    perfil = getattr(user, "profile", None)
    for campo in (getattr(perfil, "photo", None), user.photo):
        if campo:
            try:
                return campo.url
            except ValueError:
                continue
    return None
