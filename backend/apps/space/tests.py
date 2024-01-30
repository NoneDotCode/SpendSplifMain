from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from backend.apps.space.models import Space
from apps.customuser.models import CustomUser
from backend.apps.space.serializers import SpaceSerializer


class SpaceTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create_user(username='user1', email='gmail1@gmail.com', password='password1')
        self.user2 = CustomUser.objects.create_user(username='user2', email='gmail2@gmail.com', password='password2')
        self.space1 = Space.objects.create(owner=self.user1, title='space1')
        self.space2 = Space.objects.create(owner=self.user2, title='space2')

    def test_create_spaces(self):
        counter = Space.objects.count()
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/v1/create_space/', {'title': 'space3'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Space.objects.count(), counter + 1)
        self.client.force_authenticate(user=self.user2)
        response = self.client.post('/api/v1/create_space/', {'title': 'space3'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Space.objects.count(), counter + 2)

    def test_edit_spaces(self):
        counter = Space.objects.count()
        response = self.client.put(f'/api/v1/my_spaces/{self.space2.id}/', {'title': 'new_name'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(f'/api/v1/my_spaces/{self.space2.id}/', {'title': 'new_name'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.put(f'/api/v1/my_spaces/{self.space1.id}/', {'title': 'new_name'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Space.objects.get(id=self.space1.id).title, 'new_name')
        self.assertEqual(Space.objects.count(), counter)

    def test_delete_spaces(self):
        counter = Space.objects.count()
        response = self.client.delete(f'/api/v1/delete_space/{self.space2.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.login(username='user2', password='password2')
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f'/api/v1/delete_space/{self.space2.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Space.objects.count(), counter - 1)

    def test_view_spaces(self):
        counter = Space.objects.count()
        response = self.client.get('/api/v1/my_spaces/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/v1/my_spaces/')
        spaces = Space.objects.filter(owner=self.user1)
        serializer = SpaceSerializer(spaces, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(Space.objects.count(), counter)
