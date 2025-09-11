
from rest_framework import serializers

from subscription.models import Package, Subscription

# list of serielizers in subscription app

# user Subscription serielizer
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['subscription_id', 'status', 'subscription_end_date', 'registered']


# packages serializer
class PackagesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Package
        fields = ['package_id', 'amount', 'name', 'days', 'description', 'registered']