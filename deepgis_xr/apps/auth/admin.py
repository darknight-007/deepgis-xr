from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, VerificationCode

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'phone_number', 'is_phone_verified', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_phone_verified')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('phone_number',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_phone_verified'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone_number', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'phone_number')
    ordering = ('username',)

@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'user__phone_number', 'code')
    ordering = ('-created_at',) 