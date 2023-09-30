from django.db import transaction
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework.utils import json
from rest_framework import generics, status

from apps.goal.serializers import GoalSerializer
from apps.goal.models import Goal
from apps.goal.permissions import TransferToGoalPermission

from apps.account.models import Account

from apps.converter.utils import convert_currencies

from apps.account.permissions import IsOwnerOfSpace, IsInRightSpace

from apps.space.models import Space

from apps.total_balance.models import TotalBalance


class CreateGoal(generics.CreateAPIView):
    serializer_class = GoalSerializer
    permission_classes = (IsOwnerOfSpace,)

    def get_queryset(self):
        return Goal.objects.filter(father_space_id=self.kwargs.get('space_pk'))

    def create(self, request, *args, **kwargs):
        space_pk = self.kwargs.get('space_pk')
        space = get_object_or_404(Space, pk=space_pk)
        request.data['father_space'] = space.pk
        request.data['spent'] = 0
        return super().create(request, *args, **kwargs)


class EditGoal(generics.RetrieveUpdateAPIView):
    serializer_class = GoalSerializer
    permission_classes = (IsOwnerOfSpace, IsInRightSpace)

    def get_queryset(self):
        return Goal.objects.filter(pk=self.kwargs.get('pk'))


class ViewGoals(generics.ListAPIView):
    serializer_class = GoalSerializer
    permission_classes = (IsOwnerOfSpace,)

    def get_queryset(self):
        return Goal.objects.filter(father_space_id=self.kwargs.get('space_pk'))


class TransferToGoalView(generics.GenericAPIView):

    def get_queryset(self):
        return Goal.objects.filter(pk=self.kwargs.get("goal_pk"))

    serializer_class = GoalSerializer
    permission_classes = (TransferToGoalPermission,)

    @staticmethod
    def put(request, *args, **kwargs):
        space_pk = kwargs.get("space_pk")
        account_pk = request.data.get("account_pk")
        account = Account.objects.get(pk=account_pk)
        goal_pk = kwargs.get("goal_pk")
        goal = Goal.objects.get(pk=goal_pk)
        target = request.data.get("target")
        amount = request.data.get("amount")
        if target == "goal":
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
            else:
                return Response({"error": "Please, fill out row amount, numbers bigger than 0."})
        elif target == "account":
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
        else:
            return Response({"error": "You should input in target 'account' or 'goal'"})
        return Response({"success": "Transfer successfully completed."}, status=status.HTTP_200_OK)
