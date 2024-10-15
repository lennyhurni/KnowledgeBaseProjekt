from django.db import models
from django.conf import settings
from documents.models import Folder

class Chatbot(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    folders = models.ManyToManyField(Folder, related_name='chatbots')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Idle')  # Status für die Indexierung

    def __str__(self):
        return self.name