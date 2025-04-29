from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('label/', views.label, name='label'),
    path('map-label/', views.map_label, name='map_label'),
    path('view-label/', views.view_label, name='view_label'),
    path('results/', views.results, name='results'),
    
    # Webclient API endpoints
    path('webclient/getCategoryInfo', views.get_category_info, name='get_category_info'),
    path('webclient/getNewImage', views.get_new_image, name='get_new_image'),
    path('webclient/getAllImages', views.get_all_images, name='get_all_images'),
    path('webclient/saveLabel', views.save_label, name='save_label'),
    path('webclient/createCategory', views.create_category, name='create_category'),
    path('webclient/getRasterInfo', views.get_raster_info, name='get_raster_info'),
    path('webclient/getTileserverLayers', views.get_tileserver_layers, name='get_tileserver_layers'),
    
    # Map label endpoints
    path('webclient/save-labels', views.save_labels, name='save_labels'),
    path('webclient/export-shapefile', views.export_shapefile, name='export_shapefile'),
    
    # Grid detection endpoint
    path('webclient/detect-grid', views.detect_grid, name='detect_grid'),
] 