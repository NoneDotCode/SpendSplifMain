from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.account.models import Account
from apps.category.models import Category
from apps.customuser.models import CustomUser
from apps.space.models import Space
from backend.apps.total_balance.models import TotalBalance
from backend.apps.total_balance.serializers import TotalBalanceSerializer


class TotalBalanceTestCase(APITestCase):
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

    def test_convert_total_and_account(self):
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f'/api/v1/my_spaces/{self.space1.pk}/create_account/',
                                    {
                                        'title': 'account1',
                                        "balance": 23,
                                        "currency": "CZK"
                                    }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f'/api/v1/my_spaces/{self.space1.pk}/create_account/',
                                    {
                                        'title': 'account1',
                                        "balance": 36,
                                        "currency": "UAH"
                                    }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/v1/my_spaces/{self.space1.pk}/total_balance/', format='json')
        total_balance = TotalBalance.objects.filter(father_space=self.space1.pk)
        serializer = TotalBalanceSerializer(total_balance, many=True)
        self.assertEqual(response.data, serializer.data)
        # Если валюта USD, а баланс переконвертировался (+-2) - тест прошел успешно
        print(response.data)

    def test_edit_total_and_account(self):
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f'/api/v1/my_spaces/{self.space1.pk}/create_account/',
                                    {
                                        'title': 'account1',
                                        "balance": 23,
                                        "currency": "CZK"
                                    }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f'/api/v1/my_spaces/{self.space1.pk}/create_account/',
                                    {
                                        'title': 'account1',
                                        "balance": 36,
                                        "currency": "UAH"
                                    }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(f'/api/v1/my_spaces/{self.space1.pk}/total_balance/edit/',
                                   {
                                       'currency': 'UAH'
                                   }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/v1/my_spaces/{self.space1.pk}/total_balance/', format='json')
        total_balance = TotalBalance.objects.filter(father_space=self.space1.pk)
        serializer = TotalBalanceSerializer(total_balance, many=True)
        self.assertEqual(response.data, serializer.data)
        # Если валюта изменилась на UAH, а баланс переконвертировался (+-73) - тест прошел успешно
        print(response.data)
