from django.urls import path, re_path
from . import views
from . import consumers

urlpatterns = [
    path('api/chat/save/', views.SaveChatView.as_view(), name='save-chat'),
    path('api/chat/list/', views.ChatListView.as_view(), name='chat-list'),
    path('api/chat/<int:user_id>/<int:chat_id>/', views.ChatDetailView.as_view(), name='chat-detail'),
    path('api/characters/', views.CharacterListView.as_view(), name='character-list'),
    path('api/characters/<int:pk>/', views.CharacterDetailView.as_view(), name='character-detail'),
]
