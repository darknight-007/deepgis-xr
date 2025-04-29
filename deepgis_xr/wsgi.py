"""
WSGI config for deepgis_xr project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deepgis_xr.settings')

application = get_wsgi_application() 