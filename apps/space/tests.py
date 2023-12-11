from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.space.models import Space, MemberPermissions
from apps.customuser.models import CustomUser
from apps.space.serializers import SpaceSerializer


class SpaceTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create_user(username='user1', email='gmail1@gmail.com', password='password1')
        self.user2 = CustomUser.objects.create_user(username='user2', email='gmail2@gmail.com', password='password2')
        self.space1 = Space.objects.create(title='space1')
        self.space1.members.set([self.user1])
        self.space2 = Space.objects.create(title='space2')
        self.perms = MemberPermissions(member=self.user2, space=self.space2)
        self.perms.owner = True
        self.perms.save()


