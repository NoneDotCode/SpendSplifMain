from django.utils import timezone

from .serializers import ExpenseSummarySerializer, StatisticViewSerializer
from datetime import datetime, timedelta

from drf_multiple_model.views import ObjectMultipleModelAPIView

from backend.apps.goal.serializers import GoalSerializer
from backend.apps.history.models import HistoryIncome, HistoryExpense
from backend.apps.history.serializers import HistoryExpenseSerializer, DailyIncomeSerializer, \
    HistoryExpenseAutoDataSerializer, HistoryIncomeAutoDataSerializer, HistoryTransferAutoDataSerializer

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from backend.apps.history.serializers import HistoryIncomeSerializer



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


class StatisticView(generics.ListAPIView):
    serializer_class = StatisticViewSerializer

    def get_queryset(self):
        queryset = HistoryExpense.objects.exclude(to_cat__isnull=True)

        seven_days_ago = timezone.now() - timedelta(days=7)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        ninety_days_ago = timezone.now() - timedelta(days=90)
        year_ago = timezone.now() - timedelta(days=365)

        week_expenses = queryset.filter(created__gte=seven_days_ago)
        month_expenses = queryset.filter(created__gte=thirty_days_ago)
        recent_expenses = queryset.filter(created__gte=ninety_days_ago)
        year_expenses = queryset.filter(created__gte=year_ago)

        week_summary = self.calculate_summary(week_expenses)
        month_summary = self.calculate_summary(month_expenses)
        three_month_summary = self.calculate_summary(recent_expenses)
        year_summary = self.calculate_summary(year_expenses)

        formatted_result = {
            "Week": week_summary,
            "Month": month_summary,
            "3 month": three_month_summary,
            "Year": year_summary
        }

        return [formatted_result]

    def calculate_summary(self, expenses):
        summary = {}

        for to_cat in set(expense.to_cat for expense in expenses):
            category_expenses = expenses.filter(to_cat=to_cat)
            summary[to_cat] = sum([int(expense.amount) for expense in category_expenses])

        return summary

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class IncomeAutoDataView(generics.ListAPIView):
    permission_classes = ()
    serializer_class = HistoryIncomeAutoDataSerializer

    def get_queryset(self):
        father_space = self.kwargs["space_pk"]
        income_data = [
            {'amount': 1500, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 1, 1), 'comment': ''},
            {'amount': 100, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 3, 1), 'comment': ''},
            {'amount': 750, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 5, 1), 'comment': ''},
            {'amount': 1500, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 9, 1), 'comment': ''},
            {'amount': 50, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 11, 1), 'comment': ''},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 12, 1), 'comment': ''},
            {'amount': 1900, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 12, 15), 'comment': ''},
            {'amount': 500, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 12, 30), 'comment': ''},
            {'amount': 390, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 5), 'comment': ''},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 10), 'comment': ''},
            {'amount': 2000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 20), 'comment': ''},
            {'amount': 300, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 24), 'comment': ''},
            {'amount': 900, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 26), 'comment': ''},
            {'amount': 10000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 28), 'comment': ''},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 30), 'comment': ''}
        ]

        for data in income_data:
            serializer = HistoryIncomeAutoDataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseAutoDataView(generics.ListAPIView):
    permission_classes = ()
    serializer_class = HistoryExpenseAutoDataSerializer

    def get_queryset(self):
        father_space = self.kwargs["space_pk"]
        expense_data = [
            {'amount': 750, 'father_space': father_space, 'currency': 'USD', 'periodic': True,
             'from_acc': 'Cash', 'created': datetime(2023, 1, 30), 'comment': '', 'to_cat': 'Food'},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 3, 20), 'comment': '', 'to_cat': 'Home'},
            {'amount': 2000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 5, 11), 'comment': '', 'to_cat': 'Food'},
            {'amount': 750, 'father_space': father_space, 'currency': 'USD', 'periodic': True,
             'from_acc': 'Cash', 'created': datetime(2023, 9, 11), 'comment': '', 'to_cat': 'Food'},
            {'amount': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 11, 10), 'comment': '', 'to_cat': 'Home'},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 12, 2), 'comment': '', 'to_cat': 'Food'},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 12, 16), 'comment': '', 'to_cat': 'Food'},
            {'amount': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 12, 31), 'comment': '', 'to_cat': 'Home'},
            {'amount': 100, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2024, 3, 6), 'comment': '', 'to_cat': 'Food'},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2024, 3, 11), 'comment': '', 'to_cat': 'Home'},
            {'amount': 750, 'father_space': father_space, 'currency': 'USD', 'periodic': True,
             'from_acc': 'Cash', 'created': datetime(2024, 3, 21), 'comment': '', 'to_cat': 'Food'},
            {'amount': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2024, 3, 25), 'comment': '', 'to_cat': 'Food'},
            {'amount': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2024, 3, 27), 'comment': '', 'to_cat': 'Home'},
            {'amount': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2024, 3, 29), 'comment': '', 'to_cat': 'Food'},
            {'amount': 2000, 'father_space': father_space, 'currency': 'USD', 'periodic': True,
             'from_acc': 'Cash', 'created': datetime(2024, 3, 31), 'comment': ''}
        ]

        for data in expense_data:
            serializer = HistoryExpenseAutoDataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransferAutoDataView(generics.ListAPIView):
    permission_classes = ()
    serializer_class = HistoryTransferAutoDataSerializer

    def get_queryset(self):
        father_space = self.kwargs["space_pk"]
        goal_data = [
            {'title': 'main', 'goal': 4000, 'collected': 0, 'father_space': father_space},
            {'title': 'main2', 'goal': 3000, 'collected': 0, 'father_space': father_space},
        ]
        for data in goal_data:
            serializer = GoalSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        transfer_data = [
            {'amount': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 9, 11), 'to_goal': 'main'},
            {'amount': 250, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 10, 18), 'to_goal': 'main'},
            {'amount': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 7, 1), 'to_goal': 'main2'},
            {'amount': 1250, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 12, 20), 'to_goal': 'main2'},
            {'amount': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2024, 2, 15), 'to_goal': 'main2'},
        ]

        for data in transfer_data:
            serializer = HistoryTransferAutoDataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
