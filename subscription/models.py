from django.db import models

from users.models import User

# Create your models here.


# a model that defines a single package for payment
class Package(models.Model):
    package_id = models.CharField(primary_key=True, max_length=50)
    amount = models.FloatField()
    name = models.CharField(max_length=80, blank=False, null=False, unique=True,)
    days = models.IntegerField(blank=False, null=False, default=0)
    description = models.CharField(max_length=200, blank=False, null=False)
    registered = models.DateTimeField(auto_now_add=True)

    packages = models.Manager()

    class Meta:
        db_table = "packages"

# model for a user subscription data
class Subscription(models.Model):
    subscription_id = models.CharField(primary_key=True, max_length=50)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    package = models.ForeignKey(Package, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=10, default="pending")
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    registered = models.DateTimeField(auto_now_add=True)

    subscriptions = models.Manager()

    class Meta:
        db_table = "subscriptions"


# a model for a single payment transaction
class Transaction(models.Model):
    transaction_id = models.CharField(primary_key=True, max_length=50)
    transaction_number = models.CharField(unique=True, max_length=100, blank=False, null=False,)
    reference_id = models.CharField(max_length=50, blank=False, null=False, unique=True,)
    reference_type = models.CharField(max_length=100, blank=False, null=False,)
    amount = models.FloatField()
    status = models.CharField(max_length=50, default='pending')
    payment_method = models.CharField(max_length=50, blank=False, null=False,)
    payment_channel = models.CharField(max_length=50, blank=False, null=False,)
    phone_number = models.CharField(max_length=12, blank=False, null=False,)
    updated_at = models.DateTimeField(auto_now=True)
    registered = models.DateTimeField(auto_now_add=True)
    package = models.ForeignKey(Package, on_delete=models.DO_NOTHING, null=True,)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True,)

    transactions = models.Manager()

    class Meta:
        db_table = "transactions"
