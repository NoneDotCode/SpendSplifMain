from django.urls import path
from apps.messenger.views import CreateChatView, DmChatView, SpaceChatView

urlpatterns = [
    path('chat/<int:owner_1_id>/<int:owner_2_id>/', DmChatView.as_view(), name='chat'),
    path('create_chat/', CreateChatView.as_view(), name='create_chat'),
    path('my_spaces/<int:space_pk>/space_chat/', SpaceChatView.as_view(), name='space_chat')
]
