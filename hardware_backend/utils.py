import os
import uuid
from django.conf import settings


def upload_image_to_local(image_file, folder_name):
    """
    Save image to local media storage (e.g. for PythonAnywhere).
    Returns URL path (e.g. /media/products/uuid.jpg).
    """
    file_ext = os.path.splitext(image_file.name)[1] or '.jpg'
    unique_name = f"{uuid.uuid4()}{file_ext}"
    path = os.path.join(folder_name, unique_name)
    media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(str(settings.BASE_DIR), 'media'))
    media_url = getattr(settings, 'MEDIA_URL', '/media/').rstrip('/')
    full_path = os.path.join(media_root, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'wb') as f:
        for chunk in image_file.chunks():
            f.write(chunk)
    return f"{media_url}/{path}".replace('\\', '/')


def delete_local_image(image_url):
    """
    Delete an image from local media storage if the URL is a /media/ path.
    Returns True if the file was found and deleted.
    """
    if not image_url or not image_url.startswith('/media/'):
        return False
    media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(str(settings.BASE_DIR), 'media'))
    # path is e.g. /media/products/xxx.jpg -> relative path products/xxx.jpg
    rel = image_url.split('/media/', 1)[-1].lstrip('/')
    full_path = os.path.join(media_root, rel)
    if os.path.isfile(full_path):
        try:
            os.remove(full_path)
            return True
        except OSError:
            pass
    return False


def handle_image_upload(image_file, folder_name, old_image_url=None):
    """
    Save uploaded image to local media storage (for PythonAnywhere / local hosting).
    Optionally deletes the old image file if it was also stored locally.

    Args:
        image_file: The uploaded file object
        folder_name: The folder name (e.g. 'products', 'brands', 'banners')
        old_image_url: The URL of the old image to delete when replacing (optional)

    Returns:
        str: The new image URL (e.g. /media/products/uuid.jpg)
    """
    if old_image_url:
        delete_local_image(old_image_url)

    if not image_file:
        return old_image_url or ''

    return upload_image_to_local(image_file, folder_name)
