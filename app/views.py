from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import close_old_connections
from django.db import connection


from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChatRoom, Messages, User
from .serializers import (ChatRoomSerializer,
                          UserLoginSerializer, UserSignupSerializer,
                          MessageSerializer)


# Signe up a new user View
class UserSignupView(APIView):
    permission_classes = (AllowAny,)

    # Sigup user (create new object)
    def post(self, request):
        
        serializer = UserSignupSerializer(data=request.data)

        if serializer.is_valid():
            user_data = serializer.data
            User.objects.create_user(
                email=user_data['email'], 
                password=user_data['password'], 
                username=user_data['username'])

            user = authenticate(email=user_data['email'], password=user_data['password'])
            token, _ = Token.objects.get_or_create(user=user)
            user_data['id'] = user.id
            user_data['token'] = token.key
            
            connection.close()
            return Response({"message":"User Signed up successfully", "User":user_data}, status=status.HTTP_201_CREATED)
        else:
            connection.close()
            return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
    # Check if user exists or not
    def get(self, request):
        email = request.query_params.get("email")
        password = request.query_params.get("password")
        print(email + "___" + password)
        user = authenticate(email=email, password=password)
        if not user:
            connection.close()
            return Response({"message":"User does not exist"}, status=status.HTTP_204_NO_CONTENT)
        else:
            connection.close()
            return Response({"message":"User Already Exists"}, status=status.HTTP_302_FOUND)

# View for user login
class UserLoginView(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):
        req_data = request.data
        user = authenticate(email=req_data['email'], password=req_data['password'])
        if not user:
            connection.close()
            return Response({"message":"Invalid Details"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            token, _ = Token.objects.get_or_create(user=user)
            connection.close()
            return Response({
                "message":"User Logged In", 
                "User":{
                    "id":user.id,
                    "email":user.email,
                    "username":user.username,
                    "token":token.key
            }})

# Signout new user
class UserLogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        user = request.user
        response = {
            "message":"User logged out", 
            "Details":{
                "id": user.id,
                "email":user.email,
                "username":user.username
            }}
        request.user.auth_token.delete()
        connection.close()
        return Response(response, status=status.HTTP_200_OK)


class ViewChatRooms(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        user = request.user
        chatRooms = ChatRoom.objects.filter( Q(participant1_id=user.id) | Q(participant2_id=user.id))
        chatRooms_serializer = ChatRoomSerializer(chatRooms, many=True)
        resp = chatRooms_serializer.data
        if len(resp) == 0:
            connection.close()
            return Response({"message":"No chat rooms available"}, status=status.HTTP_204_NO_CONTENT)
        else:
            resp = chatRooms_serializer.data
            for chatroom in resp:
                user1 = User.objects.get(id=chatroom['participant1_id'])
                user2 = User.objects.get(id=chatroom['participant2_id'])
                chatroom['participant1_username'] = user1.username
                chatroom['participant2_username'] = user2.username
            connection.close()
            return Response({"message":"Chat rooms found", "ChatRooms":resp}, status=status.HTTP_200_OK)

class ViewUserDetails(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        
        user = request.user
        connection.close()
        return Response({
            "message":"User Details",
            "User": {
                "id": user.id,
                "email":user.email,
                "username":user.username,
            }                
        })


class PreviousMessagesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        
        user = request.user
        chatroom = ChatRoom.objects.filter(Q(participant1_id=user.id) | Q(participant2_id=user.id))
        if len(chatroom) == 0:
            connection.close()
            return Response({"message":"Invalid Chat Room"}, status=status.HTTP_400_BAD_REQUEST)
        messages = Messages.objects.filter(chat_room_id=pk)
        messages_serializer = MessageSerializer(messages, many=True)
        resp = list(messages_serializer.data)
        connection.close()
        return Response({"Messages": resp[::-1]}, status=status.HTTP_200_OK)