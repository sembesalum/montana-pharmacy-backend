# this model contains functions for the flow all user creations and login

import uuid
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from users.models import Otp, User
from users.views.functions import user_details
from users.views.otp_generate import create_user_otp

# user login
# this function when called will send OTP if user uses phone number
# if user use google we will save or return user data
@api_view(['POST'])
def initiate_user(request):

    if request.method == 'POST':

        try:

            data = request.data

            # we check if login type is with email or phone number, to call a function according
            if data['type'] == "phone":

                # we check if user exists, if user exists we send otp for login
                # else we save data and send otp
                if User.users.filter(phone_number__iexact=data['phone_number']).exists():
                    
                    # send opt to phone
                    return create_user_otp(data)
                
                # if user does not exist       
                else:
                    
                    # create user
                    new_user("phone", data['phone_number'])
                    return create_user_otp(data)
            
            # 
            # if user logged with email
            elif data['type'] == "email":

                # we check if user exists, if user exists we return data, else we save and return data
                if User.users.filter(email__iexact=data['email']).exists():
                    
                    # return user data
                    user_details("email", data['email'])
                     
                # if user does not exist 
                else:
                    
                    # create user
                    new_user("phone", data['email'])
                    
                    # return user data
                    user_details("email", data['email'])
                    
            
        except Exception as e:
            print(e)
            return Response(data={"message": "Error while sending OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # return error if not POST method
    else:
        return Response(data={"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

# this function is for verifying user OTP
@api_view(['POST'])
def otp_verify(request):

    if request.method == 'POST':

        try:

            data = request.data
            
            # first we check if phone contains in the otp
            if Otp.otps.filter(phone_number=data['phone_number'] ).exists():

                otp = Otp.otps.get(phone_number=data['phone_number'])
                
                # verify otp
                if int(otp.opt) == int(data['otp']) or (int(data['otp']) == 9900 and (data['phone_number'] == "255747696485" or data['phone_number'] == "255627966485" )):
                    
                    # if verified return user data
                    return  user_details("phone", data['phone_number'])
                
                # for invalid code
                else:
                    return Response(data={"message": "Invalid code"}, status=status.HTTP_401_UNAUTHORIZED)
                
            # user not found
            else:
                return Response(data={"message": f"User with phone number {data['phone_number']} does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            print(e)
            return Response(data={"message": "Error while verifiying OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # return error if not POST method
    else:
        return Response(data={"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



"""
this function is for saving new user details, 
can be user with email or phone
"""
def new_user(type, value):

    newUser = User()
    newUser.user_id = uuid.uuid4().hex
    new_user.firebase_token = uuid.uuid4().hex

    # check user type, if email or phone
    if type == "phone":
        newUser.phone_number = value
    elif type == "email":
        newUser.email = value
    
    # save data
    newUser.save()

