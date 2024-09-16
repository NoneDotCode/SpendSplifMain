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

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Get the start of the current month
        today = timezone.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Calculate total expenses for this month
        total_expenses = HistoryExpense.objects.filter(
            father_space_id=self.kwargs["space_pk"],
            created__gte=start_of_month
        ).aggregate(total=Sum('amount_in_default_currency'))['total'] or 0

        # Calculate total income for this month
        total_income = HistoryIncome.objects.filter(
            father_space_id=self.kwargs["space_pk"],
            created__gte=start_of_month
        ).aggregate(total=Sum('amount_in_default_currency'))['total'] or 0

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # Add the monthly totals to the response
        for item in data:
            item['total_expenses_this_month'] = total_expenses
            item['total_income_this_month'] = total_income

        return Response(data)
