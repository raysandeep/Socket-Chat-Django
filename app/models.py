from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=50)
    is_staff = models.BooleanField(default=False)       # Field necessary for a django user
    is_active = models.BooleanField(default=True)       # Field necessary for a django user
    is_superuser = models.BooleanField(default=False)   # Field necessary for a django user
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]

    objects = CustomUserManager()

    def __str__(self):
        return self.email




class ChatRoom(models.Model):
    participant1_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="participant1_id")
    participant2_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="participant2_id")
    last_message_time = models.DateTimeField()
    last_message_body = models.TextField(null=True)
    last_message_sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="last_message_sender", null=True)
    date_time_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_message_time']

class Messages(models.Model):
    chat_room_id = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="chat_room_id")
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender_id")
    receiver_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver_id")
    body = models.TextField()
    date_time_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_time_creation']

