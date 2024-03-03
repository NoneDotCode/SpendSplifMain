from drf_multiple_model.views import ObjectMultipleModelAPIView
from rest_framework import generics
from django.db.models import Sum
from django.http import JsonResponse
from rest_framework.views import APIView

from backend.apps.history.models import HistoryIncome, HistoryExpense
from backend.apps.history.serializers import HistoryIncomeSerializer, HistoryExpenseSerializer, DailyIncomeSerializer

from backend.apps.account.permissions import IsSpaceMember


class HistoryView(ObjectMultipleModelAPIView):
    permission_classes = ()

    def get_querylist(self):
        space_pk = self.kwargs["space_pk"]
        return [
            {"queryset": HistoryIncome.objects.filter(father_space_id=space_pk), "serializer_class":
                HistoryIncomeSerializer},
            {"queryset": HistoryExpense.objects.filter(father_space_id=space_pk), "serializer_class":
                HistoryExpenseSerializer}
        ]


class DailyIncomeView(generics.ListAPIView):
    permission_classes = ()
    serializer_class = DailyIncomeSerializer

    def get_queryset(self):
        space_pk = self.kwargs["space_pk"]
        incomes = (
            HistoryIncome.objects.filter(father_space_id=space_pk)
            .values('created__date')
            .annotate(total_income=Sum('amount'))
        )

        incomes_list = list(incomes)

        for income in incomes_list:
            income['date'] = income['created__date']

        return incomes_list

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)
