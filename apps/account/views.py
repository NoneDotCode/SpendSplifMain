from rest_framework import generics, status
from rest_framework.response import Response

from .models import Account
from .serializers import AccountSerializer


class CreateAccount(generics.CreateAPIView):
    serializer_class = AccountSerializer


class AllAccounts(generics.ListAPIView):
    serializer_class = AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(father_space_id=self.request.data.get())


class EditAccount(generics.RetrieveUpdateAPIView):
    serializer_class = AccountSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Account.objects.filter(pk=pk)
