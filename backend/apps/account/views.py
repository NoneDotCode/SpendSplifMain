from drf_multiple_model.views import ObjectMultipleModelAPIView
from rest_framework import generics
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from backend.apps.account.models import Account
from backend.apps.account.permissions import (IsSpaceMember, IsSpaceOwner, CanCreateAccounts, CanEditAccounts,
                                              CanDeleteAccounts, IncomePermission)
from backend.apps.account.serializers import AccountSerializer, IncomeSerializer
from backend.apps.converter.utils import convert_currencies
from backend.apps.history.models import HistoryIncome
from backend.apps.space.models import Space
from backend.apps.total_balance.models import TotalBalance
from backend.apps.total_balance.serializers import TotalBalanceSerializer


class CreateAccount(generics.CreateAPIView):
    serializer_class = AccountSerializer
    permission_classes = (IsSpaceMember & (IsSpaceOwner | CanCreateAccounts),)

    def create(self, request, *args, **kwargs):
        space_pk = self.kwargs.get('space_pk')
        space = get_object_or_404(Space, pk=space_pk)
        request.data['father_space'] = space_pk
        if not request.data['balance']:
            request.data['balance'] = 0
        total_balance = TotalBalance.objects.filter(father_space_id=space_pk)
        accounts_count = Account.objects.filter(father_space=space).count()
        if accounts_count >= 1 and not total_balance:
            total_balance = (TotalBalance.objects.create(
                balance=sum([convert_currencies(
                    amount=account.balance,
                    from_currency=account.currency,
                    to_currency=space.currency) for account in Account.objects.filter(father_space=space)]),
                father_space_id=space_pk
            ),)
        if total_balance:
            total_balance[0].balance += convert_currencies(amount=request.data['balance'],
                                                           from_currency=request.data['currency'],
                                                           to_currency=space.currency)
            total_balance[0].save()
        return super().create(request, *args, **kwargs)


class ViewAccounts(ObjectMultipleModelAPIView):
    permission_classes = (IsSpaceMember,)

    def get_querylist(self):
        space_pk = self.kwargs.get("space_pk")
        return [
            {
                "queryset": Account.objects.filter(father_space_id=space_pk).order_by("id"),
                "serializer_class": AccountSerializer
            },
            {
                "queryset": TotalBalance.objects.filter(father_space_id=space_pk),
                "serializer_class": TotalBalanceSerializer
            }
        ]


class EditAccount(generics.RetrieveUpdateAPIView):
    serializer_class = AccountSerializer
    permission_classes = (IsSpaceMember, CanEditAccounts)

    def get_object(self):
        pk = self.kwargs.get('pk')
        return Account.objects.get(pk=pk)

    def update(self, request, *args, **kwargs):
        account = self.get_object()
        new_balance = self.request.data['balance']
        account_balance = account.balance
        father_space = account.father_space
        total_balance = TotalBalance.objects.get(father_space=father_space)
        total_balance.balance -= convert_currencies(amount=(account_balance - new_balance),
                                                    from_currency=account.currency,
                                                    to_currency=father_space.currency)
        total_balance.save()
        return super().update(request, *args, **kwargs)


class DeleteAccount(generics.RetrieveDestroyAPIView):
    serializer_class = AccountSerializer
    permission_classes = (IsSpaceMember, CanDeleteAccounts)

    def get_object(self):
        pk = self.kwargs.get('pk')
        return Account.objects.get(pk=pk)

    def destroy(self, request, *args, **kwargs):
        account = self.get_object()
        father_space = account.father_space
        total_balance = TotalBalance.objects.get(father_space=father_space)
        total_balance.balance -= convert_currencies(amount=account.balance,
                                                    from_currency=account.currency,
                                                    to_currency=father_space.currency)
        total_balance.save()
        return super().destroy(request, *args, **kwargs)


class IncomeView(generics.GenericAPIView):
    def get_queryset(self):
        return Account.objects.filter(pk=self.kwargs['pk'])

    serializer_class = IncomeSerializer
    permission_classes = (IsSpaceMember, IncomePermission,)

    @staticmethod
    def put(request, *args, **kwargs):
        space_pk = kwargs.get('space_pk')
        space = Space.objects.get(pk=space_pk)
        account_pk = kwargs.get('pk')
        account = Account.objects.get(pk=account_pk)
        amount = request.data.get('amount')
        default_currency = space.currency
        if amount is not None and int(amount) > 0:
            account.balance += int(amount)
            account.save()
            comment = request.data.get("comment")
            if comment is None:
                comment = ""
            total_balance = TotalBalance.objects.filter(father_space_id=space_pk)
            if total_balance:
                total_balance[0].balance += convert_currencies(amount=amount,
                                                               from_currency=account.currency,
                                                               to_currency=default_currency)
                total_balance[0].save()

            account_data = {
                'id': account.id,
                'title': account.title,
                'balance': float(account.balance),
                'currency': account.currency,
                'included_in_total_balance': account.included_in_total_balance,
                'father_space': account.father_space.id
            }

            HistoryIncome.objects.create(
                amount=amount,
                currency=account.currency,
                amount_in_default_currency=convert_currencies(from_currency=account.currency,
                                                              amount=amount,
                                                              to_currency=default_currency),
                comment=comment,
                account=account_data,
                father_space_id=space_pk,
                new_balance=total_balance[0].balance if total_balance else 0
            )
        else:
            return Response({"error": "Please, fill out row amount, numbers bigger than 0."})
        return Response({"success": "Income successfully completed."}, status=status.HTTP_200_OK)
