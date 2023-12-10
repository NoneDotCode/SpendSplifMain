from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.account.models import Account
from apps.account.serializers import AccountSerializer
from apps.customuser.models import CustomUser
from apps.space.models import Space


class AccountTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create_user(username='user1', email='gmail1@gmail.com', password='password1')
        self.user2 = CustomUser.objects.create_user(username='user2', email='gmail2@gmail.com', password='password2')
        self.space1 = Space.objects.create(title='space1')
        self.space1.members.set([self.user1])
        self.space2 = Space.objects.create(title='space2')
        self.space2.members.set([self.user2])
        self.account1 = Account.objects.create(father_space=self.space1, title='account1',  balance=0, currency="USD")
        self.account2 = Account.objects.create(father_space=self.space2, title='account2',  balance=0, currency="USD")

    def test_create_account(self):
        counter = Account.objects.count()

        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f'/api/v1/my_spaces/{self.space1.pk}/create_account/',
                                    {'title': 'account1',  "balance": 0, "currency": "USD"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Account.objects.count(), counter + 1)

        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/v1/my_spaces/{self.space2.pk}/create_account/',
                                    {'title': 'account2', "balance": 0, "currency": "USD"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Account.objects.count(), counter + 2)

    def test_view_accounts(self):
        counter = Account.objects.count()
        response = self.client.get(f'/api/v1/my_spaces/{self.space1.pk}/space_accounts/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/v1/my_spaces/{self.space2.pk}/space_accounts/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/v1/my_spaces/{self.space1.pk}/space_accounts/')
        accounts = Account.objects.filter(father_space=self.space1.pk)
        serializer = AccountSerializer(accounts, many=True)
        self.assertEqual(response.data, serializer.data)

        self.assertEqual(Account.objects.count(), counter)

    def test_edit_account(self):
        counter = Account.objects.count()

        response = self.client.put(f'/api/v1/my_spaces/{self.space2.id}/space_accounts/{self.account2.id}/',
                                   {'title': 'new_name', "balance": 0, "currency": "USD"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(f'/api/v1/my_spaces/{self.space2.id}/space_accounts/{self.account2.id}/',
                                   {'title': 'new_name', "balance": 0, "currency": "USD"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(f'/api/v1/my_spaces/{self.space1.id}/space_accounts/{self.account1.id}/',
                                   {'title': 'new_name', "balance": 0, "currency": "USD"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Account.objects.get(id=self.account1.id).title, 'new_name')

        self.assertEqual(Account.objects.count(), counter)

    def test_delete_spaces(self):
        counter = Account.objects.count()
        response = self.client.delete(f'/api/v1/my_spaces/{self.space2.id}/delete_account/{self.account2.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(username='user2', password='password2')
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f'/api/v1/my_spaces/{self.space1.id}/delete_account/{self.account1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(username='user2', password='password2')
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f'/api/v1/my_spaces/{self.space2.id}/delete_account/{self.account2.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Account.objects.count(), counter - 1)

    def test_income_account(self):
        counter = Account.objects.count()

        response = self.client.put(f'/api/v1/my_spaces/{self.space2.id}/space_accounts/{self.account2.id}/income/',
                                   {'amount': 1})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(username='user2', password='password2')
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(f'/api/v1/my_spaces/{self.space1.id}/space_accounts/{self.account1.id}/income/',
                                   {'amount': 1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(username='user2', password='password2')
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(f'/api/v1/my_spaces/{self.space2.id}/space_accounts/{self.account2.id}/income/',
                                   {'amount': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(Account.objects.count(), counter)
