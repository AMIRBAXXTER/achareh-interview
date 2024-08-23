from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
import random

from .mixins import GetOrNoneMixin


# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The phone number must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password):
        user = self.create_user(phone_number, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin, GetOrNoneMixin):
    phone_number = models.CharField(max_length=11, unique=True, verbose_name='شماره تماس')
    first_name = models.CharField(max_length=255, verbose_name='نام')
    last_name = models.CharField(max_length=255, verbose_name='نام خانوادگی')
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'phone_number'

    def __str__(self):
        return self.phone_number

    objects = CustomUserManager()


class OTP(models.Model, GetOrNoneMixin):
    phone_number = models.CharField(max_length=11,null=True, verbose_name='شماره تماس')
    otp = models.CharField(max_length=6, null=True, blank=True, verbose_name='کد تایید')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone_number

    def save(self, *args, **kwargs):
        old_otp = OTP.get_or_none(phone_number=self.phone_number)
        if old_otp:
            old_otp.delete()
        self.otp = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() - self.created_at < timezone.timedelta(minutes=5)


class FailedLoginTry(models.Model):
    user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE, verbose_name='کاربر')
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='آی پی')
    timestamp = models.DateTimeField(default=timezone.now, verbose_name='زمان تلاش برای ورود')


class BlockedIPs(models.Model, GetOrNoneMixin):
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='آی پی')
