from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import pytz
from django.db.models.signals import pre_save
from django.dispatch import receiver

class User(AbstractUser):
    """Custom user model."""
    email = models.EmailField(unique=True)
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

@receiver(pre_save, sender=User)
def convert_to_ist(sender, instance, **kwargs):
    """Convert timestamps to IST before saving"""
    ist = pytz.timezone('Asia/Kolkata')
    
    # Convert last_login to IST
    if instance.last_login:
        if instance.last_login.tzinfo is None:
            instance.last_login = timezone.make_aware(instance.last_login)
        instance.last_login = instance.last_login.astimezone(ist)
    
    # Convert created_at to IST for new users
    if instance._state.adding and instance.created_at:
        if instance.created_at.tzinfo is None:
            instance.created_at = timezone.make_aware(instance.created_at)
        instance.created_at = instance.created_at.astimezone(ist)
    
    # Convert date_joined to IST for new users
    if instance._state.adding and instance.date_joined:
        if instance.date_joined.tzinfo is None:
            instance.date_joined = timezone.make_aware(instance.date_joined)
        instance.date_joined = instance.date_joined.astimezone(ist)
