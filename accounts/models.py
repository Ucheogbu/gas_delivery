from accounts.util import get_api_key
import uuid
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, fake_password, user_id, address, state, country, password=None):
        if not email:
            msg = 'Users must have an email address'
            raise ValueError(msg)

        if not username:
            msg = 'This username is not valid'
            raise ValueError(msg)

        if not user_id:
            msg = 'Please Verify Your user id'
            raise ValueError(msg)

        user = self.model(email=UserManager.normalize_email(email), username=username, first_name=first_name,
                          last_name=last_name, user_id=user_id, address=address, state=state, country=country, fake_password=fake_password)

        user.set_password(password)
        user.save(using=self._db)
        key = get_api_key()
        APIKey.objects.create(user=user, api_key=key)
        return user

    def create_superuser(self, first_name, last_name, username, email, user_id,fake_password, address, state, country, password):
        user = self.create_user(email, first_name, last_name, username, email, fake_password, user_id, address, state, country, password=password,)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    user_id = models.CharField(verbose_name='User ID', max_length=255)
    email = models.CharField(verbose_name='Email Address', max_length=255, unique=True)
    phone_number = models.CharField(verbose_name='Email Address', max_length=255, unique=True)
    address = models.CharField(verbose_name='Address', max_length=255)
    state = models.CharField(verbose_name='State', max_length=255)
    country = models.CharField(verbose_name='Country', max_length=255)
    password = models.CharField(verbose_name='Password', max_length=255)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username', 'country',  'user_id', 'address', 'state']

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_vendor = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=True)

    objects = UserManager()


class APIKey(models.Model):
    user = models.OneToOneField('accounts.User', related_name='user_data', on_delete=models.CASCADE)
    api_key = models.CharField(verbose_name='API Key', max_length=255)

