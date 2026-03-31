from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
import random
from datetime import timedelta
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError(_('The Phone Number must be set'))
        
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractUser):
    username = None  # Remove username field
    phone_number = models.CharField(_('phone number'), max_length=15, unique=True)
    full_name = models.CharField(_('full name'), max_length=255)
    is_verified = models.BooleanField(_('verified'), default=False)
    profile_photo = models.ImageField(
        _('profile photo'),
        upload_to='profiles/',
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.phone_number

class OTP(models.Model):
    phone_number = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        # Valid for 5 minutes
        expiration_time = self.created_at + timedelta(minutes=5)
        return timezone.now() <= expiration_time and not self.is_used

    @classmethod
    def generate_otp(cls, phone_number):
        # Invalidate old OTPs for this phone number
        cls.objects.filter(phone_number=phone_number, is_used=False).update(is_used=True)
        code = str(random.randint(100000, 999999))
        return cls.objects.create(phone_number=phone_number, code=code)

class UserFollow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return f"{self.follower} follows {self.followed}"
