from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.account.models import Account
from apps.account.serializers import AccountSerializer
from apps.account.permissions import IsOwnerOfFatherSpace, IsInRightSpace, IsOwnerOfSpace, IncomePermission

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


class IncomeView(generics.GenericAPIView):

    def get_queryset(self):
        return Account.objects.filter(pk=self.kwargs['pk'])

    serializer_class = AccountSerializer
    permission_classes = (IncomePermission,)

    @staticmethod
    def put(request, *args, **kwargs):
        space_pk = kwargs.get('space_pk')
        account_pk = kwargs.get('pk')
        account = Account.objects.get(pk=account_pk)
        amount = request.data.get('amount')
        if amount is not None and amount > 0:
            account.balance += amount
            account.save()
        else:
            return Response({"error": "Please, fill out row amount, numbers bigger than 0."})
        return Response({"success": "Income successfully completed."}, status=status.HTTP_200_OK)
