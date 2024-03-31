from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.customuser.models import CustomUser
from apps.messenger.models import DmChat, DmMessage, SpaceGroup
from apps.space.models import Space

"""
ТЕСТЫ КОТОРЫЕ НУЖНО СДЕЛАТЬ В ПОСТМЕНЕ:
1. Создать пространство, и добавить другого пользователя, проверить создается ли чат автоматически 
и могут ли они выполнять все GET и POST запросы.
"""


class MessengerTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create_user(username='user1', email='gmail1@gmail.com', password='password1')
        self.user2 = CustomUser.objects.create_user(username='user2', email='gmail2@gmail.com', password='password2')
        self.user3 = CustomUser.objects.create_user(username='user3', email='gmail3@gmail.com', password='password3')
        self.dm_chat = DmChat.objects.create(owner_1=self.user1, owner_2=self.user2,)
        self.space1 = Space.objects.create(title='space1')
        self.space1.members.set([self.user1])



#сделать тесты костельно пространственного чата
