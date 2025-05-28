from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from .constants import *


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_email_verified", True)
        extra_fields.setdefault("is_phone_verified", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_role", ADMIN)

        user = self.create_user(email, password=password, **extra_fields)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name =models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255,unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)

    country_code = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_email_otp_sent  = models.BooleanField(default=False, null=True, blank=True)

    is_email_verified = models.BooleanField(default=False, null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False, null=True, blank=True)

    last_login = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    user_role = models.IntegerField(choices=USER_ROLE, default=USER, null=True, blank=True)
    
    created_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    is_active = models.BooleanField(default=False, null=True, blank=True)
    is_admin = models.BooleanField(default=False, null=True, blank=True)
    is_staff = models.BooleanField(default=False,null=True, blank=True)
    is_superuser = models.BooleanField(default=False, null=True, blank=True)


    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "tbl_user"
        managed = True

    