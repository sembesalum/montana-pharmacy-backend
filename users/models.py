from django.db import models

# Create your models here.


# users model
class User(models.Model):
    user_id = models.CharField(max_length=50, primary_key=True)
    full_name = models.CharField(max_length=100, blank=True, null=True, )
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True,)
    email = models.CharField(max_length=100, blank=True, null=True, unique=True,)
    firebase_token = models.CharField(max_length=200, default="", blank=True, null=True, unique=False,)
    dob =  models.CharField(max_length=20, blank=True, null=True,)
    gender =  models.CharField(max_length=10, blank=True, null=True,)
    relation_goals =  models.CharField(max_length=100, blank=True, null=True,)
    interest =  models.CharField(max_length=10, blank=True, null=True,)
    activity =  models.CharField(max_length=30, blank=True, null=True,)
    registered = models.DateTimeField(auto_now_add=True, null=False,)
    ios_version = models.CharField(max_length=50, null=False, default="1.0.1")
    android_version = models.CharField(max_length=50, null=False, default="1.0.1")

    users = models.Manager()

    class Meta:
        db_table = "users"


# user location model
class UserLocation(models.Model):
    location_id = models.CharField(max_length=50, primary_key=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    accuracy = models.FloatField()
    altitude = models.FloatField()
    speed = models.FloatField()
    speedAccuracy = models.FloatField()
    heading = models.FloatField()
    time = models.FloatField()
    isMock = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False, related_name='location')

    location = models.Manager()

    class Meta:
        db_table = "location"

# images of user
# on user 
class UserImage(models.Model):
    image_id = models.CharField(max_length=50, primary_key=True)
    image = models.CharField(max_length=200, blank=False, unique=True,)
    registered = models.DateTimeField(auto_now_add=True, null=False,)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name='images', null=False,)
    image_encode = models.CharField(max_length=200, blank=False, unique=False, default="L371cr_3RKKFsqICIVNG00eR?d-r")

    images = models.Manager()

    class Meta:
        db_table = "images"

# hobbies of user
# this are list of hobbies that are defined on user registration
class UserHobbies(models.Model):
    hobbies_id = models.CharField(max_length=50, primary_key=True)
    hobbie = models.CharField(max_length=200, blank=False)
    registered = models.DateTimeField(auto_now_add=True, null=False,)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hobbies', blank=False, null=False,)
    

    hobbies = models.Manager()

    class Meta:
        db_table = "hobbies"

# user likes
# this are likes a certain user likes another person or receives likes
class Likes(models.Model):
    like_id = models.CharField(max_length=50, primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_likes', blank=False, null=False)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes', blank=False, null=False)
    registered = models.DateTimeField(auto_now_add=True, null=False,)

    likes = models.Manager()

    class Meta:
        db_table = "likes"


# model for storing user otp
class Otp(models.Model):
    phone_number = models.CharField(max_length=50, primary_key=True)
    opt = models.CharField(max_length=6)

    otps = models.Manager()
    
    class Meta:
        db_table = "otps"
