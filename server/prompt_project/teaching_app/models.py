from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class ChatMessage(models.Model):

    id = models.AutoField(primary_key=True)
    email = models.EmailField()
    user_message = models.CharField(max_length=255)
    chatgpt_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"id: {self.id}, usermessage: {self.user_message}"
