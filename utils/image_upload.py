import os
from django.views.decorators.csrf import csrf_exempt
import uuid

import boto3 as boto3


def add_media_to_s3(request, key):

    # get file
    fileToUpload = request.FILES["image"]
    fileDirectory = fileToUpload.temporary_file_path()
    uniquePictureId = uuid.uuid4().hex
    extension = fileToUpload.name.split(".")[-1].lower()

    # location for media to be uploaded
    mediaLocation = "chekaplus/" + "/" + uniquePictureId + "." + extension
    mediaUrl = "https://ejn-dev.s3.us-west-1.amazonaws.com/" + mediaLocation

    # credentials for aws account
    client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),    
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name="us-east-1"
    )

    # upload file
    client.upload_file(
        fileDirectory, 
        "ejn-dev", 
        mediaLocation,              
        ExtraArgs={'ContentType': 'image/' + extension}
    )

    return mediaUrl


@csrf_exempt
def upload_image(request, key):
    if request.method == 'POST':
        file_to_upload = request.FILES.get(key)

        if file_to_upload:
            destination_folder = "/users/images"

            # Check if the destination folder exists, create it if not
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)

            # Construct the destination path
            destination_path = os.path.join(destination_folder, file_to_upload.name)

            # Save the uploaded image to the destination folder
            with open(destination_path, 'wb') as destination_file:
                for chunk in file_to_upload.chunks():
                    destination_file.write(chunk)