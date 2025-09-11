from rest_framework import serializers

from users.models import Likes, User, UserHobbies, UserImage, UserLocation

# list of serie;lizers in user app

# user images serielizer
class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = "__all__"

# user hobbies
class HobbiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserHobbies
        fields = "__all__"

# user likes
class LikesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Likes
        fields = ['like_id', 'sender', 'receiver', 'registered']
    
# location serielizer
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = ['location_id', 'latitude', 'longitude', 'accuracy', 'altitude', 'speed', 'speedAccuracy', 'heading', 'time', 'isMock']

# user serilizer
class UserSerializer(serializers.ModelSerializer):
    images = ImagesSerializer(read_only=True, many=True)
    hobbies = HobbiesSerializer(read_only=True, many=True)
    likes = LikesSerializer(read_only=True, many=True,)

    # user location model
    location = LocationSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ['user_id', 'full_name', 'phone_number', 'email', 'dob', 'gender', 'relation_goals', 'interest', 'activity', 'registered', 'images', 'hobbies', 'likes', 'location', 'ios_version', 'android_version']


# like serielizer with user models
class LikesWithUserSerializer(serializers.ModelSerializer):

    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    class Meta:
        model = Likes
        fields = "__all__"
