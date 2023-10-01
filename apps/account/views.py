from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.account.models import Account
from apps.account.serializers import AccountSerializer
from apps.account.permissions import IsOwnerOfFatherSpace, IsInRightSpace, IsOwnerOfSpace, IncomePermission

from apps.space.models import Space

from apps.history.models import HistoryIncome

from apps.total_balance.models import TotalBalance

from apps.converter.utils import convert_currencies

from drf_multiple_model.views import ObjectMultipleModelAPIView

from apps.total_balance.models import TotalBalance
from apps.total_balance.serializers import TotalBalanceSerializer


class CreateAccount(generics.CreateAPIView):
    serializer_class = AccountSerializer
    permission_classes = (IsOwnerOfSpace,)

    def create(self, request, *args, **kwargs):
        space_pk = self.kwargs.get('space_pk')
        space = get_object_or_404(Space, pk=space_pk)
        request.data['father_space'] = space.pk
        total_balance = TotalBalance.objects.filter(father_space_id=space_pk)
        accounts_count = Account.objects.all().count()
        if accounts_count >= 1 and not total_balance:
            total_balance = list(TotalBalance.objects.create(
                balance=sum([convert_currencies(
                    amount=account.balance,
                    from_currency=account.currency,
                    to_currency=self.request.user.currency) for account in Account.objects.all()]),
                currency=self.request.user.currency,
                father_space_id=space_pk
            ))
        if total_balance:
            total_balance[0].balance += convert_currencies(amount=request.data['balance'],
                                                           from_currency=request.data['currency'],
                                                           to_currency=total_balance[0].currency)
            total_balance[0].save()
        return super().create(request, *args, **kwargs)


class ViewAccount(ObjectMultipleModelAPIView):
    serializer_class = AccountSerializer
    permission_classes = (IsOwnerOfSpace,)

    def get_querylist(self):
        space_pk = self.kwargs.get("space_pk")
        return [
            {
                "queryset": Account.objects.filter(father_space_id=space_pk),
                "serializer_class": AccountSerializer
            },
            {
                "queryset": TotalBalance.objects.filter(father_space_id=space_pk),
                "serializer_class": TotalBalanceSerializer
            }
        ]


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

    def destroy(self, request, *args, **kwargs):
        account = self.get_object()
        father_space = account.father_space
        accounts_count = Account.objects.filter(father_space=father_space).count()
        total_balance = TotalBalance.objects.filter(father_space=father_space)
        if accounts_count <= 2 and total_balance:
            total_balance.delete()
        elif accounts_count > 2 and total_balance:
            total_balance[0].balance -= convert_currencies(amount=account.balance,
                                                           from_currency=account.currency,
                                                           to_currency=total_balance[0].currency)
            total_balance[0].save()
        return super().destroy(request, *args, **kwargs)


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
            total_balance = TotalBalance.objects.filter(father_space_id=space_pk)
            if total_balance:
                total_balance[0].balance += convert_currencies(amount=amount,
                                                               from_currency=account.currency,
                                                               to_currency=total_balance[0].currency)
                total_balance[0].save()
        else:
            return Response({"error": "Please, fill out row amount, numbers bigger than 0."})
        return Response({"success": "Income successfully completed."}, status=status.HTTP_200_OK)
