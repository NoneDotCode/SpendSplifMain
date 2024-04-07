from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.messenger.models import DmChat, DmMessage, SpaceGroup
from apps.account.models import Account
from apps.account.serializers import AccountSerializer
from apps.category.models import Category
from apps.category.serializers import CategorySerializer
from apps.customuser.models import CustomUser
from apps.space.models import Space, MemberPermissions
from apps.space.serializers import SpaceSerializer
from apps.total_balance.models import TotalBalance
from apps.total_balance.serializers import TotalBalanceSerializer


class AllTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create_user(username='user1', email='gmail1@gmail.com', password='password1')
        self.user2 = CustomUser.objects.create_user(username='user2', email='gmail2@gmail.com', password='password2')
        self.user3 = CustomUser.objects.create_user(username='user3', email='gmail3@gmail.com', password='password3')
        self.dm_chat = DmChat.objects.create(owner_1=self.user1, owner_2=self.user2, )
        self.space1 = Space.objects.create(title='space1')
        self.space1.members.set([self.user1])
        self.space2 = Space.objects.create(title='space2')
        self.perms = MemberPermissions(member=self.user2, space=self.space2)
        self.perms.owner = True
        self.perms.save()
        self.account1 = Account.objects.create(father_space=self.space1, title='account1',  balance=0, currency="USD")
        self.account2 = Account.objects.create(father_space=self.space2, title='account2',  balance=0, currency="USD")
        self.category1 = Category.objects.create(father_space=self.space1, title='category1', spent=0)
        self.category2 = Category.objects.create(father_space=self.space2, title='category2', spent=0)

    def test_create_spaces(self):
        counter = Space.objects.count()

        response = self.client.post('/api/v1/create_space/', {'title': 'space3'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/v1/create_space/', {'title': 'space3'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Space.objects.count(), counter + 1)

        self.client.force_authenticate(user=self.user2)
        response = self.client.post('/api/v1/create_space/', {'title': 'space3'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Space.objects.count(), counter + 2)

        self.client.logout()

    def test_edit_spaces(self):
        counter = Space.objects.count()

        response = self.client.put(f'/api/v1/my_spaces/{self.space2.id}/', {'title': 'new_name'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(f'/api/v1/my_spaces/{self.space2.id}/', {'title': 'new_name'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(username='user2', password='password2')
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(f'/api/v1/my_spaces/{self.space2.id}/', {'title': 'new_name'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(Space.objects.get(id=self.space2.id).title, 'new_name')

        self.assertEqual(Space.objects.count(), counter)

        self.client.logout()

    def test_delete_spaces(self):
        counter = Space.objects.count()

        response = self.client.delete(f'/api/v1/delete_space/{self.space2.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(username='user2', password='password2')
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f'/api/v1/delete_space/{self.space2.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Space.objects.count(), counter - 1)

        self.client.logout()

    def test_view_spaces(self):
        counter = Space.objects.count()

        response = self.client.get('/api/v1/my_spaces/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/v1/my_spaces/')
        spaces = Space.objects.filter(members=self.user1)
        serializer = SpaceSerializer(spaces, many=True)
        self.assertEqual(response.data, serializer.data)

        self.assertEqual(Space.objects.count(), counter)

        self.client.logout()

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


        self.client.logout()

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

        self.client.logout()

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

        self.client.logout()

    def test_create_category(self):
        counter = Category.objects.count()
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            f'/api/v1/my_spaces/{self.space1.pk}/create_category/',
            {
                'title': 'category1',
                'spent': 0
             }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), counter + 1)
        self.client.login(username='user2', password='password2')
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(
            f'/api/v1/my_spaces/{self.space2.pk}/create_category/',
            {
                'title': 'category2',
                'spent': 0
            }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), counter + 2)

        self.client.logout()

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
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(Category.objects.count(), counter)

        self.client.logout()

    def test_edit_category(self):
        counter = Category.objects.count()
        response = self.client.put(f'/api/v1/my_spaces/{self.space2.id}/my_categories/{self.category2.id}/',
                                   {
                                       'title': 'new_name',
                                       "spent": 0
                                   }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(f'/api/v1/my_spaces/{self.space2.id}/my_categories/{self.category2.id}/',
                                   {
                                       'title': 'new_name',
                                       "spent": 0
                                   }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.put(f'/api/v1/my_spaces/{self.space1.id}/my_categories/{self.category1.id}/',
                                   {
                                       'title': 'new_name',
                                       "spent": 0
                                   }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Category.objects.get(id=self.category1.id).title, 'new_name')
        self.assertEqual(Category.objects.count(), counter)

        self.client.logout()

    def test_spend_to_category(self):
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(f'/api/v1/my_spaces/{self.space1.pk}/my_categories/{self.category1.pk}/spend/',
                                   {
                                       "amount": 244,
                                       "comment": "milk",
                                       "account_pk": self.account2.pk
                                   }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.put(f'/api/v1/my_spaces/{self.space1.pk}/my_categories/{self.category1.pk}/spend/',
                                   {
                                       "amount": 244,
                                       "comment": "milk",
                                       "account_pk": self.account1.pk
                                   }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_chat_creation(self):
        counter = DmChat.objects.count()

        response = self.client.post('/api/v1/create_chat/', {'owner_1': self.user2.username}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/v1/create_chat/', {'owner_1': f"{self.user2.username}#{self.user2.tag}"},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(DmChat.objects.count(), counter + 1)

        self.client.logout()

    def test_chat_post(self):
        counter = DmMessage.objects.count()
        response = self.client.post(f'/api/v1/chat/{self.user1.id}/{self.user2.id}/', {'text': 'test'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f'/api/v1/chat/{self.user1.id}/{self.user2.id}/', {'text': 'test'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.login(username='user2', password='password2')
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/v1/chat/{self.user1.id}/{self.user2.id}/', {'text': 'test2'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.login(username='user3', password='password3')
        self.client.force_authenticate(user=self.user3)
        response = self.client.post(f'/api/v1/chat/{self.user1.id}/{self.user2.id}/', {'text': 'test'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(DmMessage.objects.count(), counter + 2)

        self.client.logout()

    # сделать так, чтоб гет запрос выдавал то же самое что и в сериалайзере
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

        self.client.logout()

    def test_chat_delete(self):
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/v1/chat/{self.user1.id}/{self.user2.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

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

        self.client.logout()

    def test_get_space_group(self):
        self.space_group = SpaceGroup.objects.create(father_space_id=self.space1.id)
        self.client.login(username='user1', password='password1')
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/v1/space_chat/{self.space_group.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

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
        print(response.data)
        total_balance = TotalBalance.objects.filter(father_space=self.space1.pk)
        serializer = TotalBalanceSerializer(total_balance, many=True)
        self.assertEqual(response.data, serializer.data)
        # Если валюта USD, а баланс переконвертировался (+-2) - тест прошел успешно
        print(response.data)

        self.client.logout()

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