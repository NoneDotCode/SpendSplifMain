from rest_framework import generics

from .models import Account
from .serializers import AccountSerializer


class AllAccounts(generics.ListAPIView):
    serializer_class = AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(father_space_id=self.request.data.get('space_pk'))


class EditAccount(generics.RetrieveUpdateAPIView):
    serializer_class = AccountSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Account.objects.filter(pk=pk)
