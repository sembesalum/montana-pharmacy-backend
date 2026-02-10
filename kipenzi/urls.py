"""
URL configuration for kipenzi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users import views
from subscription import views as subViews

urlpatterns = [
    path('admin/', admin.site.urls),

    # users urls

    # auth
    path('v1/authentication', views.initiate_user),
    path('v1/auth-verification', views.otp_verify),

    # functions
    path('v1/update-profile', views.insert_data),
    path('v1/users', views.home_users),
    path('v1/user-data', views.user_data),
    path('v1/like-unlike', views.like_unlike),
    path('v1/likes', views.user_likes),

    # upload images
    path('v1/image-upload', views.upload_user_image),
    path('v1/delete-account', views.delete_account),

    # subscription
    path('v1/initiate-sub', subViews.initiate_payment),
    path('v1/activate-sub', subViews.activate_subscription),

    # Hardware Backend APIs
    path('v1/hardware/', include('hardware_backend.urls')),
    # Backwards-compatible hardware API prefix (for clients calling /hardware/...)
    path('hardware/', include('hardware_backend.urls')),
]
