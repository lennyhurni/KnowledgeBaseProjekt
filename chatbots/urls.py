from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/', views.chatbot_detail, name='chatbot_detail'),
    path('create/', views.create_chatbot, name='create_chatbot'),
    path('list/', views.chatbot_list, name='chatbot_list'),
    path('<int:chatbot_id>/configure/', views.configure_chatbot, name='configure_chatbot'),
    path('<int:chatbot_id>/delete/', views.delete_chatbot, name='delete_chatbot'),
    path('<int:chatbot_id>/interact/', views.chatbot_interact, name='chatbot_interact'),
]
