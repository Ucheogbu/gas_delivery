import uuid
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _


# Create your models here.


class Transaction(models.Model):
    transaction_id = models.CharField(_('Transaction ID'), max_length=255, default=str(uuid.uuid4()))
    wallet = models.ForeignKey("wallet.Wallet", verbose_name=_("Wallet"), related_name='transactions', on_delete=models.CASCADE, null=True)
    amount = models.FloatField(_('Amount'),  default=0.0)
    status = models.CharField(_('Status'), max_length=255, default='failed')
    reference = models.CharField(_('Reference'), max_length=255, default=str(uuid.uuid4()))
    origin = models.CharField(_('Origin'), max_length=255, default='wallet')
    trans_type = models.CharField(_('Transaction Type'), max_length=255, default='credit')
    created_at = models.DateTimeField(auto_now_add=True)


class Wallet(models.Model):
    user = models.OneToOneField('accounts.User', verbose_name=_("User"), related_name='wallet', on_delete=models.CASCADE)
    balance = models.FloatField(_('Balance'), max_length=255, default=100.0)
    wallet_id = models.CharField(verbose_name=_("Wallet ID"), max_length=255, default=str(uuid.uuid4()))


class Card(models.Model):
    user = models.ForeignKey('accounts.User', verbose_name=_("User"), related_name='cards', on_delete=models.CASCADE)
    card_id = models.CharField(verbose_name=_("card_id"), max_length=255, default=str(uuid.uuid4()))
    auth_ref = models.CharField(_('Authentication Reference'), max_length=255, unique=True, null=True)
    ref_code = models.CharField(_('Transaction Reference'), max_length=255, unique=True)
    verified = models.BooleanField(_('Verified'), default=False)
    reusable = models.BooleanField(_('Reusable'), default=False)
    card_type = models.CharField(_('Card Type'), max_length=255, null=True)
    origin = models.CharField(_('Name'), max_length=255, default='paystack')
    last4 = models.CharField(_('Last4'), max_length=255, null=True)
    exp_month = models.CharField(_('Expiry Month'), max_length=255, null=True)
    exp_year = models.CharField(_('Expiry Year'), max_length=255, null=True)
    first6 = models.CharField(_('Bin'), max_length=255, null=True)
    bank = models.CharField(_('Bank'), max_length=255, null=True)
    signature = models.CharField(_('Signature'), max_length=255, null=True)
    country_code = models.CharField(_('Country Code'), max_length=255, null=True)
    customer_id = models.IntegerField(_('Customer Id'), null=True)
