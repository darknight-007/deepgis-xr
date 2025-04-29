from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'auth'

urlpatterns = [
    path('login/', views.PhoneLoginView.as_view(), name='phone_login'),
    path('verify/', views.VerifyCodeView.as_view(), name='verify_code'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
] 