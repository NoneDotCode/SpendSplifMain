from rest_framework import status, generics
from rest_framework.response import Response

from backend.apps.account.models import Account
from backend.apps.account.serializers import AccountSerializer
from backend.apps.account.permissions import IsSpaceMember

from backend.apps.converter.utils import convert_currencies

from backend.apps.goal.models import Goal
from backend.apps.history.models import HistoryTransfer

from backend.apps.total_balance.models import TotalBalance

from backend.apps.transfer.permissions import TransferPermission


class TransferView(generics.GenericAPIView):

    def get_queryset(self):
        return Account.objects.filter(pk=self.kwargs.get("account_pk"))

    serializer_class = AccountSerializer
    permission_classes = (IsSpaceMember, TransferPermission)

    @staticmethod
    def put(request, *args, **kwargs):
        space_pk = kwargs.get("space_pk")
        from_object = request.data.get("from_object")
        to_object = request.data.get("to_object")
        amount = request.data.get("amount")
        if from_object == "goal" and to_object == "goal":
            return Response({"error": "Transfers only for account-goal, account-account, goal-account"},
                            status=status.HTTP_400_BAD_REQUEST)
        elif from_object == "goal" and to_object == "account":
            goal = Goal.objects.get(pk=request.data.get("from_goal"))
            account = Account.objects.get(pk=request.data.get("to_account"))
            from_currency = request.user.currency
            if TotalBalance.objects.filter(father_space_id=space_pk):
                from_currency = TotalBalance.objects.filter(father_space_id=space_pk)[0].currency
            if amount is not None and amount > 0:
                if amount > goal.collected:
                    return Response({"error": "You have not enough money collected."})
                goal.collected -= amount
                account.balance += convert_currencies(amount=amount,
                                                      from_currency=from_currency,
                                                      to_currency=account.currency)
                account.save()
                goal.save()
                HistoryTransfer.objects.create(from_goal=goal.title,
                                               to_acc=account.title,
                                               father_space_id=space_pk,
                                               amount=amount,
                                               amount_in_default_currency=amount,
                                               currency=from_currency)
                return Response({"success": "Transfer successfully completed."}, status=status.HTTP_200_OK)
        elif from_object == "account" and to_object == "goal":
            goal = Goal.objects.get(pk=request.data.get("to_goal"))
            account = Account.objects.get(pk=request.data.get("from_account"))
            to_currency = request.user.currency
            if TotalBalance.objects.filter(father_space_id=space_pk):
                to_currency = TotalBalance.objects.filter(father_space_id=space_pk)[0].currency
            if amount is not None and amount > 0:
                if amount > account.balance:
                    return Response({"error": "You have not enough money on the account."})
                account.balance -= amount
                goal.collected += convert_currencies(amount=amount,
                                                     from_currency=account.currency,
                                                     to_currency=to_currency)
                account.save()
                goal.save()
                HistoryTransfer.objects.create(from_acc=account.title,
                                               to_goal=goal.title,
                                               father_space_id=space_pk,
                                               amount_in_default_currency=convert_currencies(from_currency=account.currency,
                                                   amount=amount,
                                                   to_currency=to_currency),
                                               amount=amount,
                                               currency=to_currency)
                return Response({"success": "Transfer successfully completed."}, status=status.HTTP_200_OK)
        elif from_object == "account" and to_object == "account":
            from_account = Account.objects.get(pk=request.data.get("from_account"))
            to_account = Account.objects.get(pk=request.data.get("to_account"))
            currency = request.user.currency
            if TotalBalance.objects.filter(father_space_id=space_pk):
                currency = TotalBalance.objects.filter(father_space_id=space_pk)[0].currency
            if amount is not None and amount > 0:
                if amount > from_account.balance:
                    return Response({"error": "You have not enough money on the account."})
                from_account.balance -= amount
                to_account.balance += convert_currencies(amount=amount,
                                                         from_currency=from_account.currency,
                                                         to_currency=to_account.currency)
                from_account.save()
                to_account.save()
                HistoryTransfer.objects.create(from_acc=from_account.title,
                                               to_acc=to_account.title,
                                               father_space_id=space_pk,
                                               amount=amount,
                                               amount_in_default_currency=convert_currencies(from_currency=from_account.currency,
                                                                                             amount=amount,
                                                                                             to_currency=currency),
                                               currency=currency,
                                               )
                return Response({"success": "Transfer successfully completed."}, status=status.HTTP_200_OK)
