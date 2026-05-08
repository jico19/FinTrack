from django.urls import path
from . import views

urlpatterns = [
    path('coach/', views.chatbot_view, name='chatbot_view'),
    path('send-message/', views.send_message, name='send_message'),
    path('clear-chat/', views.clear_chat, name='clear_chat'),
]
