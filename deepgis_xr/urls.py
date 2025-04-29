from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from deepgis_xr.apps.web import views as web_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Web interface
    path('', include('deepgis_xr.apps.web.urls')),
    
    # Authentication URLs
    path('auth/', include('deepgis_xr.apps.auth.urls')),
    
    # API endpoints
    path('api/v1/', include('deepgis_xr.apps.api.v1.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)