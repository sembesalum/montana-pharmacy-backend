import base64
import hmac
import json
import requests
from datetime import timezone, timedelta
import datetime


def get_keys(array):
    return ",".join(array.keys())

# 
def digest_creds(timestamp, api_secret, array):
    toDigest = "timestamp=" + timestamp
    for key in array.keys():
        toDigest += "&" + key + "=" + array[key]

    return base64.b64encode(
        hmac.digest(api_secret.encode(), toDigest.encode(), 'sha256')).decode()

def testSelcom():
    api_key = "TILL61073438-1056ab9dec2627bfcef3c84ee6bfbc7e"
    api_secret = "cb1472-e52e71-ff100d-e36bcc-ea30a2-a2cd0b"
    tz = timezone(timedelta(hours=3))
    current_time = datetime.datetime.now(tz)
    timestamp = str(current_time.isoformat())

    # api_digest = digest_creds(timestamp, api_secret,)
    array = {}
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

    url = "https://apigw.selcommobile.com/v1/imt/wallet-namelookup?utilitycode=MPREMITIN&utilityref=255747696485&transid=535571da-ae2a-11ef-9cd2-0242ac120002"

    request = requests.get(url=url, data=json.dumps(array), headers=headers)

    response = json.loads(request.text)

    print(response)


testSelcom()