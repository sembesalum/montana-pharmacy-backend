# this model contains list of function that are used general

import random
from users.models import Otp
from rest_framework.response import Response
from rest_framework import status
import requests
import json


def create_user_otp(data):
    try:
        
        # delete otp is exists
        Otp.otps.filter(phone_number=data['phone_number']).delete()

        # create a new otp and save
        otp = generate_otp(data['phone_number'])
        saveOtp = Otp()
        saveOtp.phone_number = data['phone_number']
        saveOtp.opt = otp
        saveOtp.save()

        return Response(data={"message": "OTP sent"}, status=status.HTTP_200_OK)
    
    except Exception as e:
            print(e)
            return Response(data={"message": f"Error while sending OTP, {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# generate otp and send a message to the phone number
def generate_otp(phone_number):

    # generate a random number
    opt = 1234  # Default OTP for testing

    # send a message with the OTP
    url = "http://50.18.89.52:8000/users/send-otp/"

    message = f"Welcome To Kipenzi!\nThank you for using our service \nyour OTP is {opt}"

    payload = json.dumps({
                "otp": opt,
                "phone": phone_number,
                "user": "KIPENZI", 
                "pwd": "kipenzi@2024", 
                "number": phone_number,
                "sender": "Kipenzi",
                "msg": message,
                "language": "Unicode"
                }
            )
    headers = {
        'Content-Type': 'application/json',
        "accept": "application/json",
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    json_response = json.loads(response.text)

    return opt