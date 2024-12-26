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
    path('webclient/saveLabel', views.save_label, name='save_label'),
    path('webclient/createCategory', views.create_category, name='create_category'),
] 