from django.apps import AppConfig

class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'deepgis_xr.apps.auth'
    label = 'deepgis_auth'  # Use a unique label to avoid conflicts with django.contrib.auth 