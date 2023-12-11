from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.account.models import Account
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
        self.account1 = Account.objects.create(father_space=self.space1, title='account1',  balance=400, currency="USD")
        self.account2 = Account.objects.create(father_space=self.space2, title='account2',  balance=400, currency="USD")
        self.category1 = Category.objects.create(father_space=self.space1, title='category1', spent=0)
        self.category2 = Category.objects.create(father_space=self.space2, title='category2', spent=0)



