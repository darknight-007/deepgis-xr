from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('label/', views.label, name='label'),
    path('map-label/', views.map_label, name='map_label'),
    path('view-label/', views.view_label, name='view_label'),
    path('results/', views.results, name='results'),
] 