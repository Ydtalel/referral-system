import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone
from django.core.cache import cache

from referrals.utils import CACHE_KEY_PREFIX


class UserProfile(AbstractUser):
    """
    Модель для расширения стандартного пользователя
    """

    groups = models.ManyToManyField(
        Group,
        related_name='userprofile_groups',
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='userprofile_permissions',
        blank=True,
        help_text='Specific permissions for this user.'
    )
    referred_by = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='referrals'
    )
    email = models.EmailField(unique=True)


class ReferralCode(models.Model):
    """
    Модель для хранения реферальных кодов
    """

    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='referral_codes',
        on_delete=models.CASCADE
    )
    expiration_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.is_active:
            ReferralCode.objects.filter(user=self.user, is_active=True).update(
                is_active=False)
        else:
            cache.delete(f"{CACHE_KEY_PREFIX}{self.code}")
        super().save(*args, **kwargs)
        cache.set(f"{CACHE_KEY_PREFIX}{self.code}", self, timeout=None)

    def is_expired(self):
        """
        Проверяет, истек ли срок действия кода
        """
        return timezone.now() > self.expiration_date

    def __str__(self):
        return f"Referral code for {self.user.username}: {self.code}"
