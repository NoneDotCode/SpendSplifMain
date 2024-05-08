from django.urls import path
from apps.messenger.views import CreateChatView, DmChatView, SpaceChatView, MessengerSetSettingsWhoCanText

urlpatterns = [
    path('chat/<int:owner_1_id>/<int:owner_2_id>/', DmChatView.as_view(), name='chat'),
    path('create_chat/', CreateChatView.as_view(), name='create_chat'),
    path('space_chat/<int:group_id>/', SpaceChatView.as_view(), name='space_chat'),
    path('messenger/get/<int:user_id>/', MessengerSetSettingsWhoCanText.as_view(), name='messenger_get_user'),
    path('messenger/set_settings/<int:user_id>/<int:settings>/<int:notification>/', MessengerSetSettingsWhoCanText.as_view(), name='messenger-settings'),
]
