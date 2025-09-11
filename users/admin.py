from django.contrib import admin

from users.models import Likes, Otp, User, UserHobbies, UserImage

# Register your models here.
admin.site.register(User)
admin.site.register(UserImage)
admin.site.register(UserHobbies)
admin.site.register(Likes)
admin.site.register(Otp)