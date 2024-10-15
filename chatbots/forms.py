from django import forms
from .models import Chatbot

class ChatbotForm(forms.ModelForm):
    class Meta:
        model = Chatbot
        fields = ('name', 'folders')
        widgets = {
            'folders': forms.CheckboxSelectMultiple(),
        }

class ChatbotConfigForm(forms.ModelForm):
    class Meta:
        model = Chatbot
        fields = ('name', 'folders')
        widgets = {
            'folders': forms.CheckboxSelectMultiple(),
        }
