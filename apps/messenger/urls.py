from django.urls import path
from apps.messenger.views import CreateChatView, ChatView

urlpatterns = [
    path('chat/<int:owner_1_id>/<int:owner_2_id>/', ChatView.as_view(), name='chat'),
    path('create_chat/', CreateChatView.as_view(), name='create_chat'),
]
