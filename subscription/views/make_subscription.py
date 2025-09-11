"""
This function is for making subscription
"""
import base64
import hmac
import json
import requests
import uuid
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from subscription.models import Package, Subscription, Transaction
from datetime import timezone, timedelta
import datetime
from users.models import User


# this function initiates a payment request using Swahilies API
@api_view(['POST'])
def initiate_payment(request):

    if request.method == 'POST':

        try:

            data = request.data

            # make request to Swahilies API
            transactionId = uuid.uuid4().hex

            selcom_payment_data = {
                "order_id": transactionId,
                "amount": str(data['amount']),
                "vendor": "TILL61073438",
                "buyer_email": "kipenziapp@gmail.com",
                "buyer_name": "Erick Justin",
                "buyer_phone": data['phone'],
                "currency": "TZS",
                "webhook": base64.b64encode("https://ec2-13-52-26-24.us-west-1.compute.amazonaws.com/v1/activate-sub".encode()).decode(),
                "no_of_items": "1"
            }

            jsonResponse = make_selcom_payment_order(selcom_payment_data, transactionId)
            

            if jsonResponse['code'] == 200:

                # get package
                package = Package.packages.get(package_id=data['package'])
                # get user
                user =  User.users.get(user_id=data['user_id'])

                # save data to the transaction model
                transaction = Transaction()
                transaction.transaction_id = transactionId
                transaction.transaction_number = uuid.uuid4().hex
                transaction.reference_id = jsonResponse['selcom']['reference']
                transaction.reference_type = "Selcom"
                transaction.amount = int(data['amount'])
                transaction.payment_method = "mobile_money"
                transaction.payment_channel = ""
                transaction.phone_number = data['phone']
                transaction.package = package
                transaction.user = user
                
                transaction.save()


                # json to return
                return_data = {
                    "message": "Payment Initialized, Please Wait for push popup ",
                }
                

                return Response(data=return_data, status=status.HTTP_200_OK)

            else:

                return_data = {
                    "message": "There was an issue making payment request",
                }
                

                return Response(data=return_data, status=status.HTTP_502_BAD_GATEWAY)
                    
            
        except Exception as e:
            print(e)
            return Response(data={"message": "Error while sending OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # return error if not POST method
    else:
        return Response(data={"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


"""
    Make selcom payment
"""
def make_selcom_payment_order(data, transid):
    api_key = "TILL61073438-1056ab9dec2627bfcef3c84ee6bfbc7e"
    api_secret = "cb1472-e52e71-ff100d-e36bcc-ea30a2-a2cd0b"
    tz = timezone(timedelta(hours=3))
    current_time = datetime.datetime.now(tz)
    timestamp = str(current_time.isoformat())

    # api_digest = digest_creds(timestamp, api_secret,)
    array = data
    api_digest = digest_creds(timestamp, api_secret, array)

    headers = {
        'content-type': 'application/json',
        "accept": "application/json",
        "Authorization": "SELCOM " + base64.b64encode(api_key.encode()).decode(),
        "Digest": api_digest,
        "Digest-Method": "HS256",
        "Timestamp": timestamp,
        "Signed-Fields": get_keys(array)
    }

    url = "https://apigw.selcommobile.com/v1/checkout/create-order-minimal"

    request = requests.post(url=url, data=json.dumps(array), headers=headers)

    response = json.loads(request.text)


    if response["result"] == "SUCCESS":
        data = {
            'transid': transid,
            "order_id": array['order_id'],
            "msisdn": array["buyer_phone"]
        }

        # 
        process_selcom_order(data)
        response['reference'] = response['data'][0]['payment_token']

        return {
            'code': 200,
            "transaction_id":transid,
            "msg": "Order Created And Payment Intialized \n Please Wait for push popup",
            "selcom": response
        }
    else:
        return {'code': 300, "msg": "Error1", "selcom": request.text}

# 
def digest_creds(timestamp, api_secret, array):
    toDigest = "timestamp=" + timestamp
    for key in array.keys():
        toDigest += "&" + key + "=" + array[key]

    return base64.b64encode(
        hmac.digest(api_secret.encode(), toDigest.encode(), 'sha256')).decode()

def get_keys(array):
    return ",".join(array.keys())

"""
    Process selcom order
"""
def process_selcom_order(data):
    api_key = "TILL61073438-1056ab9dec2627bfcef3c84ee6bfbc7e"
    api_secret = "cb1472-e52e71-ff100d-e36bcc-ea30a2-a2cd0b"
    tz = timezone(timedelta(hours=3))
    current_time = datetime.datetime.now(tz)
    timestamp = str(current_time.isoformat())

    array = data
    api_digest = digest_creds(timestamp, api_secret, array)

    headers = {
        'content-type': 'application/json',
        "accept": "application/json",
        "Authorization": "SELCOM " + base64.b64encode(api_key.encode()).decode(),
        "Digest": api_digest,
        "Digest-Method": "HS256",
        "Timestamp": timestamp,
        "Signed-Fields": get_keys(array)
    }

    url = "https://apigw.selcommobile.com/v1/checkout/wallet-payment"

    request = requests.post(url=url, data=json.dumps(array), headers=headers)

    response = json.loads(request.text)

    if response["result"] == "SUCCESS":

        return json.dumps({
            'code': 200, 
            "msg": "Order Created And Payment Intialized \n Please Wait for push popup",
            "selcom": request.text
        })
    else:

        return json.dumps({'code': 300, "msg": "Error"})


"""
This model is for receiving webhook and activate user subscription
"""
@api_view(['POST'])
def activate_subscription(request):

    if request.method == 'POST':

        try:

            data = request.data

            # received webhook from swahilies

            # check if transaction exists
            if Transaction.transactions.filter(transaction_id=data['order_id']).exists():

                # get transactio 
                transaction = Transaction.transactions.get(transaction_id=data['order_id'])

                # subscription end date
                package = Package.packages.get(package_id=transaction.package.package_id)
                
                subscription_end_date = datetime.datetime.now() + timedelta(days=package.days)

                print(subscription_end_date)

                # add a new user subscription
                subscription = Subscription()
                subscription.subscription_id = uuid.uuid4().hex
                subscription.user = transaction.user
                subscription.package = transaction.package
                subscription.status = "active"
                subscription.subscription_end_date = subscription_end_date
                subscription.save()

                # update transaction data
                transaction.status = "paid"
                transaction.updated_at = datetime.datetime.now()
                transaction.save()

                return Response(data={"message": "Success"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(e)
            return Response(data={"message": "Error while sending OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # return error if not POST method
    else:
        return Response(data={"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)