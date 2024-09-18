from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from backend.apps.total_balance.models import TotalBalance
from backend.apps.total_balance.serializers import TotalBalanceSerializer
from backend.apps.account.permissions import IsSpaceMember
from backend.apps.history.models import HistoryExpense, HistoryIncome


class ViewTotalBalance(generics.ListAPIView):
    serializer_class = TotalBalanceSerializer
    permission_classes = (IsSpaceMember,)

    def get_queryset(self):
        return TotalBalance.objects.filter(father_space_id=self.kwargs["space_pk"])
