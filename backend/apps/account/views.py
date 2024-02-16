from rest_framework import generics, status
from rest_framework.response import Response

from backend.apps.account.models import Account
from backend.apps.account.serializers import AccountSerializer, IncomeSerializer
from backend.apps.account.permissions import (IsSpaceMember, IsSpaceOwner, CanCreateAccounts, CanEditAccounts,
                                              CanDeleteAccounts, IncomePermission)

from backend.apps.history.models import HistoryIncome


class CreateAccount(generics.CreateAPIView):
    serializer_class = AccountSerializer
    permission_classes = (IsSpaceMember & (IsSpaceOwner | CanCreateAccounts),)

    def create(self, request, *args, **kwargs):
        space_pk = self.kwargs.get('space_pk')
        request.data['father_space'] = space_pk
        return super().create(request, *args, **kwargs)


class ViewAccounts(generics.ListAPIView):
    serializer_class = AccountSerializer
    permission_classes = (IsSpaceMember,)

    def get_queryset(self):
        return Account.objects.filter(father_space_id=self.kwargs.get("space_pk"))


class EditAccount(generics.RetrieveUpdateAPIView):
    serializer_class = AccountSerializer
    permission_classes = (IsSpaceMember, CanEditAccounts)

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Account.objects.filter(pk=pk)


class DeleteAccount(generics.RetrieveDestroyAPIView):
    serializer_class = AccountSerializer
    permission_classes = (IsSpaceMember, CanDeleteAccounts)

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Account.objects.filter(pk=pk)


class IncomeView(generics.GenericAPIView):

    def get_queryset(self):
        return Account.objects.filter(pk=self.kwargs['pk'])

    serializer_class = IncomeSerializer
    permission_classes = (IsSpaceMember, IncomePermission,)

    @staticmethod
    def put(request, *args, **kwargs):
        space_pk = kwargs.get('space_pk')
        account_pk = kwargs.get('pk')
        account = Account.objects.get(pk=account_pk)
        amount = request.data.get('amount')
        if amount is not None and int(amount) > 0:
            account.balance += int(amount)
            account.save()
            comment = request.data.get("comment")
            if comment is None:
                comment = ""
            HistoryIncome.objects.create(
                amount=amount,
                currency=account.currency,
                comment=comment,
                account=account,
                father_space_id=space_pk
            )
        else:
            return Response({"error": "Please, fill out row amount, numbers bigger than 0."})
        return Response({"success": "Income successfully completed."}, status=status.HTTP_200_OK)
