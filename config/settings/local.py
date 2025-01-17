from .base import *  # noqa
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000000
DEBUG = True
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="1jApFXEoYIJls9giiDsxDZ9Xipl53Nrxl5RhSlg3Ixf7fzlpJv2UnJB6NtGyj9Qs",
)
ALLOWED_HOSTS = ["*"]

# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]

if env("USE_DOCKER") == "yes":
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = type("c", (), {"__contains__": lambda *a: True})()

# django-extensions
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["django_extensions"]  # noqa F405

# EMAIL
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_TIMEOUT = 3600
EMAIL_USE_TLS = False
EMAIL_HOST = env("EMAIL_HOST", default="mailhog")
EMAIL_PORT = env("EMAIL_PORT", default="1025")

# Celery
# ------------------------------------------------------------------------------
CELERY_TASK_EAGER_PROPAGATES = True
# django-debug-toolbar
if env.get_value("USE_DJANGO_DEBUG_TOOLBAR", default="no") == "yes":
    INSTALLED_APPS += ["debug_toolbar"]  # F405
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa F405
    # https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
    DEBUG_TOOLBAR_CONFIG = {
        "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
        "SHOW_TEMPLATE_CONTEXT": True,
    }

# EMAIL
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_TIMEOUT = 3600
EMAIL_USE_TLS = False
EMAIL_HOST = env("EMAIL_HOST", default="mailhog")
EMAIL_PORT = env("EMAIL_PORT", default="1025")
