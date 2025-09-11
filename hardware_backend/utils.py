import boto3
import os
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import tempfile

S3_REGION = 'us-west-1'
S3_BUCKET = 'momoabucket'

def upload_image_to_s3(image_file, folder_name):
    """
    Upload image to AWS S3 and return the URL
    
    Args:
        image_file: The uploaded file object
        folder_name: The folder name in S3 (e.g., 'brands', 'products', 'banners')
    
    Returns:
        str: The S3 URL of the uploaded image
    """
    s3_client = boto3.client(
        's3', 
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=S3_REGION
    )
    
    try:
        # Generate unique filename
        file_extension = os.path.splitext(image_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        s3_key = f"{folder_name}/{unique_filename}"
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in image_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        # Upload to S3
        s3_client.upload_file(
            temp_file_path, 
            S3_BUCKET, 
            s3_key,
            ExtraArgs={'ContentType': image_file.content_type}
        )
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        # Return the S3 URL
        s3_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
        print(f"Image uploaded to S3: {s3_url}")
        return s3_url
        
    except Exception as e:
        print(f'Error uploading image to S3: {e}')
        return None

def delete_image_from_s3(image_url):
    """
    Delete image from AWS S3
    
    Args:
        image_url: The S3 URL of the image to delete
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not image_url or f'{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com' not in image_url:
        return False
    
    s3_client = boto3.client(
        's3', 
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=S3_REGION
    )
    
    try:
        # Extract the key from the URL
        s3_key = image_url.replace(f'https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/', '')
        
        # Delete from S3
        s3_client.delete_object(Bucket=S3_BUCKET, Key=s3_key)
        print(f"Image deleted from S3: {image_url}")
        return True
        
    except Exception as e:
        print(f'Error deleting image from S3: {e}')
        return False

def handle_image_upload(image_file, folder_name, old_image_url=None):
    """
    Handle image upload with cleanup of old image
    
    Args:
        image_file: The uploaded file object
        folder_name: The folder name in S3
        old_image_url: The URL of the old image to delete (optional)
    
    Returns:
        str: The new S3 URL of the uploaded image
    """
    # Delete old image if it exists
    if old_image_url:
        delete_image_from_s3(old_image_url)
    
    # Upload new image
    if image_file:
        return upload_image_to_s3(image_file, folder_name)
    
    return old_image_url 