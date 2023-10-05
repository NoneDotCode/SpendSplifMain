from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.account.models import Account
from apps.account.serializers import AccountSerializer
from apps.category.models import Category
from apps.category.serializers import CategorySerializer
from apps.customuser.models import CustomUser
from apps.space.models import Space


class CategoryTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create_user(username='user1', email='gmail1@gmail.com', password='password1')
        self.user2 = CustomUser.objects.create_user(username='user2', email='gmail2@gmail.com', password='password2')
        self.space1 = Space.objects.create(owner=self.user1, title='space1')
        self.space2 = Space.objects.create(owner=self.user2, title='space2')
        self.account1 = Account.objects.create(father_space=self.space1, title='account1',  balance=0, currency="USD")
        self.account2 = Account.objects.create(father_space=self.space2, title='account2',  balance=0, currency="USD")
        self.category1 = Category.objects.create(father_space=self.space1, title='category1', spent=0)
        self.category2 = Category.objects.create(father_space=self.space2, title='category2', spent=0)

    def test_create_category(self):
        counter = Category.objects.count()
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            f'/api/v1/my_spaces/{self.space1.pk}/create_category/',
            {'title': 'category1', 'spent': 0},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), counter + 1)

        self.client.force_authenticate(user=self.user2)
        response = self.client.post(
            f'/api/v1/my_spaces/{self.space2.pk}/create_category/',
            {'title': 'category2', 'spent': 0},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), counter + 2)

    def test_view_category(self):
        counter = Category.objects.count()
        response = self.client.get(f'/api/v1/my_spaces/{self.space1.pk}/my_categories/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/v1/my_spaces/{self.space2.pk}/my_categories/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/v1/my_spaces/{self.space1.pk}/my_categories/')
        categories = Category.objects.filter(father_space=self.space1.pk)
        serializer = CategorySerializer(categories, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(Category.objects.count(), counter)

    def test_edit_category(self):
        counter = Category.objects.count()
        response = self.client.put(f'/api/v1/my_spaces/{self.space2.id}/my_categories/{self.category2.id}/',
                                   {'title': 'new_name', "spent": 0}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(f'/api/v1/my_spaces/{self.space2.id}/my_categories/{self.category2.id}/',
                                   {'title': 'new_name', "spent": 0}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.put(f'/api/v1/my_spaces/{self.space1.id}/my_categories/{self.category1.id}/',
                                   {'title': 'new_name', "spent": 0}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Category.objects.get(id=self.category1.id).title, 'new_name')
        self.assertEqual(Category.objects.count(), counter)


