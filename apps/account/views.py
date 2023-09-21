from rest_framework import generics
from rest_framework.generics import get_object_or_404

from apps.account.models import Account
from apps.account.serializers import AccountSerializer
from apps.account.permissions import IsOwnerOfFatherSpace, IsInRightSpace, IsOwnerOfSpace

from apps.space.models import Space


class CreateAccount(generics.CreateAPIView):
    serializer_class = AccountSerializer
    permission_classes = (IsOwnerOfSpace,)

    def create(self, request, *args, **kwargs):
        space_pk = self.kwargs.get('space_pk')
        space = get_object_or_404(Space, pk=space_pk)
        request.data['father_space'] = space.pk
        return super().create(request, *args, **kwargs)


class ViewAccount(generics.ListAPIView):
    serializer_class = AccountSerializer
    permission_classes = (IsOwnerOfSpace,)

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
