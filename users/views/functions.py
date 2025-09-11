"""
List of functions used in users view
"""
from rest_framework.response import Response
from rest_framework import status
from subscription.models import Package
from subscription.serializers import PackagesSerializer
from subscription.views import check_for_valid_subscription

"""
This functions returns data for the user with email
"""
from users.models import User
from users.serializers import UserSerializer


def user_details(filterType, value):

    # pull user according
    if filterType == "email":
        user = User.users.get(email=value)
    elif filterType == "phone":
        user = User.users.get(phone_number=value)
    
    # pull by userId
    elif filterType == "user_id":
        user = User.users.get(user_id=value)
                
    # return user data
    user_serializer = UserSerializer(user)

    # subscription data
    subscriptionData = check_for_valid_subscription(user.user_id)

    # return list of packages
    packages = Package.packages.all()
    packages_serializer = PackagesSerializer(packages, many=True).data

    # json to return
    return_data = {
        "message": "user details",
        "user": user_serializer.data,
        "subscription": subscriptionData,
        "packages": packages_serializer,
    }

    return Response(data=return_data, status=status.HTTP_200_OK)