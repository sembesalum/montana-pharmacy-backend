import datetime
from subscription.models import Subscription
from subscription.serializers import SubscriptionSerializer

"""
This function is for checking is user has active subscription
"""

def check_for_valid_subscription(user_id):

    # variable for current date
    currentDate = datetime.datetime.now()

    # pull all subscriptions with the paid status
    subscriptions = Subscription.subscriptions.filter(user_id=user_id, status="active").order_by("-registered")
    if subscriptions:

        # get lates subscription
        subscription = subscriptions.order_by("-registered").first()
        if subscription.subscription_end_date.date() >= currentDate.date():
            return {
                "active": True,
                "subscription_data":  SubscriptionSerializer(subscription).data
            }
        else:
            return {
                "active": False,
            }

    else:
        return {
                "active": False,
            }