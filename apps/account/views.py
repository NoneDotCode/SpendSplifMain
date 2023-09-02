from rest_framework import generics

from apps.account.models import Account
from apps.account.serializers import AccountSerializer
from apps.account.permissions import IsOwnerOfFatherSpace, IsInRightSpace


class CreateAccount(generics.CreateAPIView):
    serializer_class = AccountSerializer


class ViewAccount(generics.ListAPIView):
    serializer_class = AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(father_space_id=self.kwargs.get("space_pk"))


class EditAccount(generics.RetrieveUpdateAPIView):
    serializer_class = AccountSerializer
    permission_classes = (IsOwnerOfFatherSpace, IsInRightSpace)

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Account.objects.filter(pk=pk)


class DeleteAccount(generics.RetrieveDestroyAPIView):
    serializer_class = AccountSerializer
    permission_classes = (IsOwnerOfFatherSpace, IsInRightSpace)

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Account.objects.filter(pk=pk)
