from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('label/', views.label, name='label'),
    path('map-label/', views.map_label, name='map_label'),
    path('view-label/', views.view_label, name='view_label'),
    path('results/', views.results, name='results'),
    
    # API endpoints
    path('api/get_available_layers.json', views.get_available_layers, name='get_available_layers'),
    path('api/get_category_info.json', views.get_category_info, name='get_category_info'),
    path('api/get_new_image.json', views.get_new_image, name='get_new_image'),
    path('api/save_label.json', views.save_label, name='save_label'),
    path('api/create_category.json', views.create_category, name='create_category'),
] 