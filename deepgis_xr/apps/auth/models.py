from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings

class User(AbstractUser):
    """Custom user model with phone number authentication"""
    phone_number = PhoneNumberField(unique=True, verbose_name=_('phone number'))
    is_phone_verified = models.BooleanField(
        default=False,
        verbose_name=_('phone verified'),
        help_text=_('Designates whether this user has verified their phone number.')
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username or str(self.phone_number)

class VerificationCode(models.Model):
    """Model to store phone verification codes"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='verification_codes'
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('verification code')
        verbose_name_plural = _('verification codes') 