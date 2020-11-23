from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SessionsConfig(AppConfig):
    name = "neural.training"
    verbose_name = _("Training")
