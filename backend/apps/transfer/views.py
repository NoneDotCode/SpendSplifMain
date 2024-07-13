from rest_framework import status, generics
from rest_framework.response import Response

from backend.apps.account.models import Account
from backend.apps.account.permissions import IsSpaceMember

from backend.apps.converter.utils import convert_currencies

from backend.apps.goal.models import Goal
from backend.apps.history.models import HistoryTransfer


from backend.apps.transfer.permissions import TransferPermission
from backend.apps.transfer.serializers import TransferGoalToAccSerializer, TransferAccToAccSerializer, TransferAccToGoalSerializer

class TransferGoalToAccView(generics.UpdateAPIView):
    serializer_class = TransferGoalToAccSerializer
    permission_classes = (IsSpaceMember, TransferPermission)
    def put(self, request, *args, **kwargs) -> Response:

        goal = Goal.objects.get(pk=request.data.get("from_goal"))
        account = Account.objects.get(pk=request.data.get("to_account"))
        from_currency = account.father_space.currency
        amount = request.data.get("amount")
        space_pk = kwargs.get("space_pk")

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
                                            currency=from_currency,
                                            goal_amount = goal.goal,
                                            collected = goal.collected,
                                            goal_is_done=None)
            return Response({"success": "Transfer successfully completed."}, status=status.HTTP_200_OK)
        
class TransferAccToGoalView(generics.UpdateAPIView):
    serializer_class = TransferAccToAccSerializer
    permission_classes = (IsSpaceMember, TransferPermission)
    def put(self, request, *args, **kwargs) -> Response:
        goal = Goal.objects.get(pk=request.data.get("to_goal"))
        account = Account.objects.get(pk=request.data.get("from_account"))
        to_currency = account.father_space.currency
        amount = request.data.get("amount")
        space_pk = kwargs.get("space_pk")

        if amount is not None and amount > 0:
            if amount > account.balance:
                return Response({"error": "You have not enough money on the account."})
            account.balance -= amount
            goal.collected += convert_currencies(amount=amount,
                                                    from_currency=account.currency,
                                                    to_currency=to_currency)
            account.save()
            goal.save()
            goal_is_done = False
            if goal.collected >= goal.goal:
                goal_is_done = True
            HistoryTransfer.objects.create(from_acc=account.title,
                                            to_goal=goal.title,
                                            father_space_id=space_pk,
                                            amount_in_default_currency=convert_currencies(from_currency=account.currency,
                                                amount=amount,
                                                to_currency=to_currency),
                                            goal_amount = goal.goal,
                                            collected = goal.collected,
                                            amount=amount,
                                            currency=to_currency,
                                            goal_is_done=goal_is_done)
            if goal_is_done:
                goal.delete()
            return Response({"success": "Transfer successfully completed."}, status=status.HTTP_200_OK)

class TransferAccToAccView(generics.UpdateAPIView):
    serializer_class = TransferAccToGoalSerializer
    permission_classes = (IsSpaceMember, TransferPermission)
    def put(self, request, *args, **kwargs) -> Response:
        from_account = Account.objects.get(pk=request.data.get("from_account"))
        to_account = Account.objects.get(pk=request.data.get("to_account"))
        currency = from_account.father_space.currency
        amount = request.data.get("amount")
        space_pk = kwargs.get("space_pk")

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
                                            goal_amount = None,
                                            collected = None,
                                            currency=currency,
                                            goal_is_done=None
                                            )
            return Response({"success": "Transfer successfully completed."}, status=status.HTTP_200_OK)
