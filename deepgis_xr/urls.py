from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('auth/', include('deepgis_xr.apps.auth.urls')),
    
    # API endpoints
    path('api/v1/', include('deepgis_xr.apps.api.v1.urls')),
    
    # Web interface
    path('', include('deepgis_xr.apps.web.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)