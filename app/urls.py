from django.urls import path, include
from .views import (
    UserSignupView,
    UserLoginView,
    UserLogoutView,
    ViewChatRooms,
    ViewUserDetails,
    PreviousMessagesView,
)
from rest_framework import routers

router = routers.DefaultRouter()


urlpatterns = [
    path("login/", UserLoginView.as_view()),
    path("signup/", UserSignupView.as_view()),
    path("logout/", UserLogoutView.as_view()),
    path("view_chat_rooms/", ViewChatRooms.as_view()),
    path("view_user_details/", ViewUserDetails.as_view()),
    path("previous_messages/<int:pk>/", PreviousMessagesView.as_view()),
]