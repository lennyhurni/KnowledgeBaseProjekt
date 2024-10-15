from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Chatbot
from documents.models import Folder

class ChatbotTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='password')
        self.folder = Folder.objects.create(name='Testordner', owner=self.user)

    def test_create_chatbot(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post('/chatbots/create/', {'name': 'Testbot', 'folders': [self.folder.id]})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Chatbot.objects.filter(name='Testbot').exists())

    def test_delete_chatbot(self):
        chatbot = Chatbot.objects.create(name='Testbot', owner=self.user)
        self.client.login(username='testuser', password='password')
        response = self.client.post(f'/chatbots/delete/{chatbot.id}/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Chatbot.objects.filter(id=chatbot.id).exists())