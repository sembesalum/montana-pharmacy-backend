
from django.contrib import admin
from subscription.models import Subscription, Transaction, Package

# Register your models here.
admin.site.register(Package)
admin.site.register(Subscription)
admin.site.register(Transaction)