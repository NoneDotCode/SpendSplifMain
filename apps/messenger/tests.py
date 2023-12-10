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

    def test_chat_creation(self):
        counter = DmChat.objects.count()

        response = self.client.post('/api/v1/create_chat/', {'owner_1': self.user2.username}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/v1/create_chat/', {'owner_1': f"{self.user2.username}#{self.user2.tag}"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(DmChat.objects.count(), counter + 1)

    def test_chat_post(self):
        counter = DmMessage.objects.count()
        response = self.client.post(f'/api/v1/chat/{self.user1.id}/{self.user2.id}/', {'text': 'test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f'/api/v1/chat/{self.user1.id}/{self.user2.id}/', {'text': 'test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.login(username='user2', password='password2')
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/v1/chat/{self.user1.id}/{self.user2.id}/', {'text': 'test2'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.login(username='user3', password='password3')
        self.client.force_authenticate(user=self.user3)
        response = self.client.post(f'/api/v1/chat/{self.user1.id}/{self.user2.id}/', {'text': 'test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(DmMessage.objects.count(), counter + 2)

#сделать так, чтоб гет запрос выдавал то же самое что и в сериалайзере
    def test_chat_get(self):
        counter = DmMessage.objects.count()
        response = self.client.get(f'/api/v1/chat/{self.user1.id}/{self.user2.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/v1/chat/{self.user1.id}/{self.user2.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.login(username='user2', password='password2')
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/api/v1/chat/{self.user1.id}/{self.user2.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.login(username='user3', password='password3')
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(f'/api/v1/chat/{self.user1.id}/{self.user2.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(DmMessage.objects.count(), counter)

    def test_chat_delete(self):
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/v1/chat/{self.user1.id}/{self.user2.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_space_group(self):
        counter = SpaceGroup.objects.count()

        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/v1/create_space/', {'title': 'test_space'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(f"/api/v1/my_spaces/{self.space1.id}/add_member/",
                                   {"user_pk": self.user2.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put(f"/api/v1/my_spaces/{self.space1.id}/add_member/",
                                   {"user_pk": self.user3.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(SpaceGroup.objects.count(), counter + 1)

    def test_get_space_group(self):
        self.space_group = SpaceGroup.objects.create(father_space_id=self.space1.id)
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/v1/space_chat/{self.space_group.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

#сделать тесты костельно пространственного чата
