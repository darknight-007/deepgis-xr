from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class AuthConfig(AppConfig):
    name = 'deepgis_xr.apps.auth'
    label = 'deepgis_auth'
    verbose_name = _('Authentication')

    def ready(self):
        try:
            import deepgis_xr.apps.auth.signals  # noqa
        except ImportError:
            pass 