"""
This model returns users like and function for liking
"""

from users.models import Likes, User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import uuid

from users.serializers import LikesSerializer, LikesWithUserSerializer
    

@api_view(['POST'])
def like_unlike(request):

    if request.method == 'POST':

        try:

            data = request.data

            # check if user exists
            if User.users.filter(user_id__iexact=data['sender_id']).exists():
                
                # unlike profile
                if Likes.likes.filter(sender_id=data['sender_id'], receiver_id=data['receiver_id']).exists():
                    like = Likes.likes.get(sender_id=data['sender_id'], receiver_id=data['receiver_id'])
                    like.delete()

                    # json to return
                    return_data = {
                        "message": "Unliked",
                    }

                    return Response(data=return_data, status=status.HTTP_200_OK)
                
                # like profile
                else:

                    sender = User.users.get(user_id=data['sender_id'])
                    receiver = User.users.get(user_id=data['receiver_id'])
                    like_id = uuid.uuid4().hex

                    like = Likes()
                    like.sender = sender
                    like.receiver = receiver
                    like.like_id = like_id
                    like.save()

                    # get like
                    like = Likes.likes.get(like_id = like_id)
                    like_serializer = LikesSerializer(like).data


                    # json to return
                    return_data = {
                        "message": "Liked",
                        "like": like_serializer,
                    }

                    return Response(data=return_data, status=status.HTTP_200_OK)

            else: # user not found
                return Response(data={"message": f"User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        
        except Exception as e:
            print(e)
            return Response(data={"message": "Error while sending OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # return error if not POST method
    else:
        return Response(data={"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



"""
Function to pull user likes

    - pull likes which user has received
"""

@api_view(['POST'])
def user_likes(request):

    if request.method == 'POST':

        try:

            data = request.data

            # check if user exists
            if User.users.filter(user_id__iexact=data['user_id']).exists():
                
                # pull user likes
                likes = Likes.likes.filter(receiver=data['user_id'])

                # user serialization
                likes_serialization = LikesWithUserSerializer(likes,  many=True).data

                 # json to return
                return_data = {
                    "message": "likes",
                    "likes": likes_serialization
                }

                return Response(data=return_data, status=status.HTTP_200_OK)

            else: # user not found
                return Response(data={"message": f"User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        
        except Exception as e:
            print(e)
            return Response(data={"message": "Error while sending OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # return error if not POST method
    else:
        return Response(data={"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)