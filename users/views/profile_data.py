from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
import uuid

from users.models import User, UserHobbies, UserImage, UserLocation
from users.serializers import UserSerializer
from users.views.functions import user_details

"""
This module has functions for inserting and return user profile data
"""


# this functions receives user profile data and saves it
@api_view(['POST'])
@csrf_exempt
def insert_data(request):

    if request.method == 'POST':

        try:

            data = request.data

            # check if user exists
            if User.users.filter(user_id__iexact=data['user_id']).exists():

                # get user data
                user = User.users.get(user_id=data['user_id'])


                # update user personal data
                user.dob = data['dob']
                user.full_name = data['name']
                user.gender = data['gender']
                user.relation_goals = data['relation_goals']
                user.interest = data['interest']
                user.activity = data['activity']
                user.save()

                # save user hobbies
                for hobbie in data['hobbies'].split(','):
                    userHobbie = UserHobbies()
                    userHobbie.hobbies_id = uuid.uuid4().hex
                    userHobbie.user = user
                    userHobbie.hobbie = hobbie.encode('utf-8').decode('unicode_escape')
                    userHobbie.save()

                # json to return
                return_data = {
                    "message": "Data saved",
                }

                return Response(data=return_data, status=status.HTTP_200_OK)

            else: # user not found
                return Response(data={"message": f"User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        
        except Exception as e:
            print(e)
            return Response(data={"message": "Error while updating user details, please try again"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # return error if not POST method
    else:
        return Response(data={"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


# this function is for returning user profiles
@api_view(['POST'])
def home_users(request):

    if request.method == 'POST':

        try:

            data = request.data
            # check if user exists
            if User.users.filter(user_id__iexact=data['user_id']).exists():

                user = User.users.get(user_id=data['user_id'])
                
                # TODO: add filters and randomization
                users = User.users.exclude(user_id__iexact=data['user_id']).exclude(gender=user.gender).exclude(full_name=None)

                # user serialization
                user_serialization = UserSerializer(users,  many=True).data

                 # json to return
                return_data = {
                    "message": "users",
                    "user": user_serialization
                }

                return Response(data=return_data, status=status.HTTP_200_OK)

            else: # user not found
                return Response(data={"message": f"User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        
        except Exception as e:
            print(e)
            return Response(data={"message": "Error while sending OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # return error if not POST method
    else:
        return Response(data={"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


# Function returns specific user data
@api_view(['POST'])
def user_data(request):

    if request.method == 'POST':

        try:

            data = request.data
            
            # check if user exists
            if User.users.filter(user_id=data['user_id']).exists():

                # user 
                user = User.users.get(user_id=data['user_id'])
                
                # location json from request
                jsonLocation = data['location']

                # check is specific user has any location
                if UserLocation.location.filter(user_id=data['user_id']).exists():

                    # update location data
                    userLocation = UserLocation.location.get(user_id=data['user_id'])
                    userLocation.latitude = jsonLocation['latitude']
                    userLocation.longitude = jsonLocation['longitude']
                    userLocation.accuracy = jsonLocation['accuracy']
                    userLocation.altitude = jsonLocation['altitude']
                    userLocation.speed = jsonLocation['speed']
                    userLocation.speedAccuracy = jsonLocation['speedAccuracy']
                    userLocation.heading = jsonLocation['heading']
                    userLocation.time = jsonLocation['time']
                    userLocation.isMock = jsonLocation['isMock']
                    userLocation.save()
                
                else: # new location

                    # update location data
                    userLocation = UserLocation()
                    userLocation.location_id = uuid.uuid4().hex
                    userLocation.user = user
                    userLocation.latitude = jsonLocation['latitude']
                    userLocation.longitude = jsonLocation['longitude']
                    userLocation.accuracy = jsonLocation['accuracy']
                    userLocation.altitude = jsonLocation['altitude']
                    userLocation.speed = jsonLocation['speed']
                    userLocation.speedAccuracy = jsonLocation['speedAccuracy']
                    userLocation.heading = jsonLocation['heading']
                    userLocation.time = jsonLocation['time']
                    userLocation.isMock = jsonLocation['isMock']
                    userLocation.save()
                    
                
                # return user data
                return  user_details("user_id", data['user_id'])
            
            else: # user not found
                return Response(data={"message": f"User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            print(e)
            return Response(data={"message": "Error while getting user data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # return error if not POST method
    else:
        return Response(data={"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


"""
    This function is for uploading single image for user
"""
@api_view(['POST'])
@csrf_exempt
def upload_user_image(request):

    if request.method == 'POST':

        try:

            data = request.data

            # check if user exists
            if User.users.filter(user_id__iexact=data['user_id']).exists():

                # get user data
                user = User.users.get(user_id=data['user_id'])

                # add data to the db
                image = UserImage()
                image.image_id = uuid.uuid4().hex
                image.image = data['image_url']
                image.image_encode = data['image_encode']
                image.user = user
                image.save()

                # json to return
                return_data = {
                    "message": "Image uploaded",
                }

                return Response(data=return_data, status=status.HTTP_200_OK)

            else: # user not found
                return Response(data={"message": f"User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        
        except Exception as e:
            print(e)
            return Response(data={"message": "Error while updating user details, please try again"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # return error if not POST method
    else:
        return Response(data={"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

@api_view(['POST'])
def delete_account(request):

    if request.method == 'POST':

        try:

            data = request.data
            
            # check if user exists
            if User.users.filter(user_id__iexact=data['user_id']).exists():

                # get user data
                user = User.users.get(user_id=data['user_id'])

                user.delete()
                    
                
                # json to return
                return_data = {
                    "message": "Deleted account"
                }

                return Response(data=return_data, status=status.HTTP_200_OK)
                
            # user not found
            else:
                return Response(data={"message": f"User with phone number {data['user_id']} does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            print(e)
            return Response(data={"message": "Error while deleting user account"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # return error if not POST method
    else:
        return Response(data={"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)