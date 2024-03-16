from typing import Dict, List, Tuple, Union
from django.utils import timezone
from .serializers import ExpenseSummarySerializer, IncomeStatisticViewSerializer, \
    CategoryViewSerializer, ExpensesViewSerializer, GoalTransferStatisticSerializer
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from drf_multiple_model.views import ObjectMultipleModelAPIView

from backend.apps.goal.serializers import GoalSerializer
from backend.apps.history.models import HistoryIncome, HistoryExpense, HistoryTransfer
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


class StatisticView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        categories_view = CategoryStatisticView.as_view()(request._request, *args, **kwargs)
        incomes_view = IncomeStatisticView.as_view()(request._request, *args, **kwargs)
        expenses_view = ExpensesStatisticView.as_view()(request._request, *args, **kwargs)
        goal_view = GoalTransferStatisticView.as_view()(request._request, *args, **kwargs)
        combined_data = {
            "Categories": categories_view.data,
            "Incomes": incomes_view.data,
            "Expenses": expenses_view.data,
            "Goals": goal_view.data,
        }
        return Response(combined_data)


class CategoryStatisticView(generics.ListAPIView):
    serializer_class = CategoryViewSerializer

    def get_queryset(self) -> List[HistoryExpense]:
        queryset = HistoryExpense.objects.exclude(to_cat__isnull=True).filter(father_space=self.kwargs['space_pk'])
        periods = [
            (7, "week"),
            (30, "month"),
            (90, "three_month"),
            (365, "year"),
        ]
        expenses = {
            period: queryset.filter(created__gte=timezone.now() - timedelta(days=days))
            for days, period in periods
        }
        return expenses

    def get_summary_and_percentages(
        self, expenses: List[HistoryExpense]
    ) -> Tuple[Dict[str, float], Dict[str, int]]:
        expenses = [expense for expense in expenses if expense.to_cat]
        total = sum(expense.amount_in_default_currency for expense in expenses)
        summary = {
            expense.to_cat: sum(
                expense.amount_in_default_currency
                for expense in expenses
                if expense.to_cat == category
            )
            for expense in expenses
            for category in {expense.to_cat}
        }
        percentages = {}
        for category, value in summary.items():
            percentage = round(value / total * 100)
            percentages[category] = percentage
        remaining_percentage = 100 - sum(percentages.values())
        if remaining_percentage != 0:
            sorted_percentages = sorted(
                percentages.items(), key=lambda x: x[1], reverse=True
            )
            largest_category, _ = sorted_percentages[0]
            percentages[largest_category] += remaining_percentage
        percentages = {
            category: f"{value}%" for category, value in percentages.items()
        }
        return summary, percentages

    def add_currency(
        self, data: Union[Dict, Decimal], currency: str
    ) -> Union[Dict, str]:
        if isinstance(data, Decimal):
            return f"{data} {currency}"
        else:
            return {
                key: f"{value} {currency}"
                if isinstance(value, (int, float, Decimal))
                else self.add_currency(value, currency)
                for key, value in data.items()
            }

    def list(self, request, *args, **kwargs):
        expenses = self.get_queryset()
        formatted_result = {}
        for period, period_expenses in expenses.items():
            summary, percentages = self.get_summary_and_percentages(period_expenses)
            formatted_result[period.capitalize()] = self.add_currency(
                summary, request.user.currency
            )
            formatted_result[f"{period.capitalize()}_Percent"] = percentages
            max_spending_category = max(summary, key=summary.get)
            formatted_result[
                f"Analyze_{period.capitalize()}"
            ] = f"This {period}, you spend most on {max_spending_category} category"
        serializer = self.get_serializer(formatted_result, many=False)
        return Response(serializer.data)


class IncomeStatisticView(generics.ListAPIView):
    serializer_class = IncomeStatisticViewSerializer

    def get_queryset(self) -> List[HistoryIncome]:
        return HistoryIncome.objects.filter(father_space=self.kwargs['space_pk'])

    def get_periods(self, incomes: List[HistoryIncome]) -> Dict[str, List[HistoryIncome]]:
        now = timezone.now()
        week_ago = now - timezone.timedelta(days=7)
        month_ago = now - timezone.timedelta(days=30)
        three_month_ago = now - timezone.timedelta(days=90)
        year_ago = now - timezone.timedelta(days=365)
        periods = {
            'week': [],
            'month': [],
            'three_month': [],
            'year': [],
        }
        for income in incomes:
            days_since_creation = (now - income.created).days
            if days_since_creation < 7:
                periods['week'].append(income)
            elif days_since_creation < 30:
                periods['month'].append(income)
            elif days_since_creation < 90:
                periods['three_month'].append(income)
            else:
                periods['year'].append(income)
        return periods

    def get_summary_and_percentages(
        self, incomes: List[HistoryIncome]
    ) -> Tuple[Dict[str, float], Dict[str, int]]:
        total = sum(income.amount_in_default_currency for income in incomes)
        summary = {
            income.created.date().isoformat(): income.amount_in_default_currency
            for income in incomes
        }
        percentages = {}
        for date, value in summary.items():
            percentage = round(value / total * 100)
            percentages[date] = percentage
        remaining_percentage = 100 - sum(percentages.values())
        if remaining_percentage != 0:
            sorted_percentages = sorted(
                percentages.items(), key=lambda x: x[1], reverse=True
            )
            if sorted_percentages:
                largest_date, _ = sorted_percentages[0]
                percentages[largest_date] += remaining_percentage
        percentages = {date: f"{value}%" for date, value in percentages.items()}
        return summary, percentages

    def add_currency(
        self, data: Union[Dict, Decimal], currency: str
    ) -> Union[Dict, str]:
        if isinstance(data, Decimal):
            return f"{data} {currency}"
        else:
            return {
                key: f"{value} {currency}"
                if isinstance(value, (int, float, Decimal))
                else self.add_currency(value, currency)
                for key, value in data.items()
            }

    def list(self, request, *args, **kwargs):
        incomes = self.get_queryset()
        periods = self.get_periods(incomes)
        formatted_result = {}
        for period, period_incomes in periods.items():
            summary, percentages = self.get_summary_and_percentages(period_incomes)
            formatted_result[period.capitalize()] = self.add_currency(
                summary, request.user.currency
            )
            formatted_result[f"{period.capitalize()}_Percent"] = percentages
            if summary:
                max_income_date = max(summary, key=summary.get)
                max_income_value = summary[max_income_date]
                formatted_result[
                    f"Analyze_{period.capitalize()}"
                ] = f"For this {period} the most {max_income_value} {request.user.currency} you earned on {max_income_date}"
            else:
                formatted_result[
                    f"Analyze_{period.capitalize()}"
                ] = f"For this {period} you did not receive any income."
        serializer = self.get_serializer(formatted_result, many=False)
        return Response(serializer.data)


class ExpensesStatisticView(generics.ListAPIView):
    serializer_class = ExpensesViewSerializer

    def get_queryset(self):
        return HistoryExpense.objects.filter(father_space=self.kwargs['space_pk'])

    def get_periods(self, expenses: List[HistoryExpense]) -> Dict[str, List[HistoryExpense]]:
        now = timezone.now()
        week_ago = now - timezone.timedelta(days=7)
        month_ago = now - timezone.timedelta(days=30)
        three_month_ago = now - timezone.timedelta(days=90)
        year_ago = now - timezone.timedelta(days=365)
        periods = {
            'week': [],
            'month': [],
            'three_month': [],
            'year': [],
        }
        for expense in expenses:
            days_since_creation = (now - expense.created).days
            if days_since_creation < 7:
                periods['week'].append(expense)
            if days_since_creation < 30:
                periods['month'].append(expense)
            if days_since_creation < 90:
                periods['three_month'].append(expense)
            if days_since_creation >= 90:
                periods['year'].append(expense)
        return periods

    def get_summary_and_percentages(self, expenses: List[HistoryExpense]) -> Tuple[Dict[str, Decimal], Dict[str, str]]:
        category_expenses = sum(expense.amount for expense in expenses if expense.to_cat)
        loss_expenses = sum(expense.amount for expense in expenses if not expense.to_cat)
        recurring_expenses = sum(expense.amount for expense in expenses if expense.periodic)
        total_expenses = category_expenses + loss_expenses + recurring_expenses
        summary = {
            'Category': category_expenses,
            'Loss': loss_expenses,
            'Recurring Spending': recurring_expenses,
        }
        if total_expenses == 0:
            percentages = {
                'Category': '0 %',
                'Loss': '0 %',
                'Recurring Spending': '0 %',
            }
        else:
            percentages = {
                'Category': f"{round((category_expenses / total_expenses) * 100)} %",
                'Loss': f"{round((loss_expenses / total_expenses) * 100)} %",
                'Recurring Spending': f"{round((recurring_expenses / total_expenses) * 100)} %",
            }
        return summary, percentages

    def analyze_expenses(self, expenses: List[HistoryExpense], period: str) -> str:
        summary, percentages = self.get_summary_and_percentages(expenses)
        max_category = max(percentages, key=percentages.get)
        return f"The most you've spent this {period} on {max_category}"

    def list(self, request, *args, **kwargs):
        expenses = self.get_queryset()
        periods = self.get_periods(expenses)
        currency = expenses.first().currency if expenses else 'USD'
        result = {}
        for period, period_expenses in periods.items():
            summary, percentages = self.get_summary_and_percentages(period_expenses)
            summary_with_currency = {key: f"{val} {currency}" for key, val in summary.items()}
            result[period] = summary_with_currency
            result[f'{period}_percent'] = percentages
            result[f'analyze_{period}'] = self.analyze_expenses(period_expenses, period)
        serializer = self.get_serializer(result)
        return Response(serializer.data)


class GoalTransferStatisticView(generics.ListAPIView):
    serializer_class = GoalTransferStatisticSerializer

    def get_queryset(self) -> List[HistoryTransfer]:
        return HistoryTransfer.objects.exclude(to_goal__isnull=True).exclude(to_goal__exact='').filter(father_space=self.kwargs['space_pk'])

    def get_periods(self, transfers: List[HistoryTransfer]) -> Dict[str, List[HistoryTransfer]]:
        now = timezone.now().replace(tzinfo=None)
        week_ago = now - timezone.timedelta(days=7)
        month_ago = now - timezone.timedelta(days=30)
        three_month_ago = now - timezone.timedelta(days=90)
        year_ago = now - timezone.timedelta(days=365)
        periods = {
            'week': [],
            'month': [],
            'three_month': [],
            'year': [],
        }
        for transfer in transfers:
            created = transfer.created.replace(tzinfo=None)
            days_since_creation = (now - created).days
            if days_since_creation < 7:
                periods['week'].append(transfer)
                periods['month'].append(transfer)
                periods['three_month'].append(transfer)
                periods['year'].append(transfer)
            elif days_since_creation < 30:
                periods['month'].append(transfer)
                periods['three_month'].append(transfer)
                periods['year'].append(transfer)
            elif days_since_creation < 90:
                periods['three_month'].append(transfer)
                periods['year'].append(transfer)
            else:
                periods['year'].append(transfer)
        return periods

    def get_summary(self, transfers: List[HistoryTransfer]) -> Dict[str, str]:
        summary = {}
        for transfer in transfers:
            goal = transfer.to_goal
            amount = Decimal(str(transfer.amount))
            currency = transfer.currency
            if goal not in summary:
                summary[goal] = f"{amount} {currency}"
            else:
                existing_amount = Decimal(summary[goal].split()[0])
                summary[goal] = f"{existing_amount + amount} {currency}"
        return summary

    def get_percentages(self, transfers: List[HistoryTransfer]) -> Dict[str, str]:
        total_amount = sum(transfer.amount for transfer in transfers)
        goal_amounts = {}
        for transfer in transfers:
            goal = transfer.to_goal
            amount = transfer.amount
            goal_amounts.setdefault(goal, 0)
            goal_amounts[goal] += amount
        percentages = {}
        for goal, amount in goal_amounts.items():
            percentage = round(amount / total_amount * 100)
            percentages[goal] = f"{percentage}%"
        return percentages

    def list(self, request, *args, **kwargs):
        transfers = self.get_queryset()
        periods = self.get_periods(transfers)
        result = {}
        for period, period_transfers in periods.items():
            summary = self.get_summary(period_transfers)
            percentages = self.get_percentages(period_transfers)
            result[period] = summary
            result[f"{period}_percent"] = percentages
        serializer = self.get_serializer(result)
        return Response(serializer.data)


class IncomeAutoDataView(generics.ListAPIView):
    permission_classes = ()
    serializer_class = HistoryIncomeAutoDataSerializer

    def get_queryset(self):
        father_space = self.kwargs["space_pk"]
        income_data = [
            {'amount': 1500, 'amount_in_default_currency': 1500, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 1, 1), 'comment': ''},
            {'amount': 100, 'amount_in_default_currency': 100, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 3, 1), 'comment': ''},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 5, 1), 'comment': ''},
            {'amount': 1500, 'amount_in_default_currency': 1500, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 9, 1), 'comment': ''},
            {'amount': 50, 'amount_in_default_currency': 50, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 11, 1), 'comment': ''},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 12, 1), 'comment': ''},
            {'amount': 1900, 'amount_in_default_currency': 1900, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 12, 15), 'comment': ''},
            {'amount': 500, 'amount_in_default_currency': 500, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 12, 30), 'comment': ''},
            {'amount': 390, 'amount_in_default_currency': 390, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 5), 'comment': ''},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 10), 'comment': ''},
            {'amount': 2000, 'amount_in_default_currency': 2000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 20), 'comment': ''},
            {'amount': 300, 'amount_in_default_currency': 300, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 24), 'comment': ''},
            {'amount': 900, 'amount_in_default_currency': 900, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 26), 'comment': ''},
            {'amount': 10000, 'amount_in_default_currency': 10000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 28), 'comment': ''},
            {'amount': 1000, 'amount_in_default_currency': 100, 'father_space': father_space, 'currency': 'USD',
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
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD', 'periodic': True,
             'from_acc': 'Cash', 'created': datetime(2023, 1, 30), 'comment': '', 'to_cat': 'Food'},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 3, 20), 'comment': '', 'to_cat': 'Home'},
            {'amount': 2000, 'amount_in_default_currency': 2000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 5, 11), 'comment': '', 'to_cat': 'Food'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD', 'periodic': True,
             'from_acc': 'Cash', 'created': datetime(2023, 9, 11), 'comment': '', 'to_cat': 'Food'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 11, 10), 'comment': '', 'to_cat': 'Home'},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 12, 2), 'comment': '', 'to_cat': 'Food'},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 12, 16), 'comment': '', 'to_cat': 'Food'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 12, 31), 'comment': '', 'to_cat': 'Home'},
            {'amount': 100, 'amount_in_default_currency': 100, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2024, 3, 6), 'comment': '', 'to_cat': 'Food'},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2024, 3, 11), 'comment': '', 'to_cat': 'Home'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD', 'periodic': True,
             'from_acc': 'Cash', 'created': datetime(2024, 3, 21), 'comment': '', 'to_cat': 'Food'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2024, 3, 25), 'comment': '', 'to_cat': 'Food'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2024, 3, 27), 'comment': '', 'to_cat': 'Home'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2024, 3, 29), 'comment': '', 'to_cat': 'Food'},
            {'amount': 2000, 'amount_in_default_currency': 2000, 'father_space': father_space, 'currency': 'USD', 'periodic': True,
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
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 9, 11), 'to_goal': 'main'},
            {'amount': 250, 'amount_in_default_currency': 250, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 10, 18), 'to_goal': 'main'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 7, 1), 'to_goal': 'main2'},
            {'amount': 1250, 'amount_in_default_currency': 1250, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2023, 12, 20), 'to_goal': 'main2'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': 'Cash', 'created': datetime(2024, 2, 15), 'to_goal': 'main2'},
        ]

        for data in transfer_data:
            serializer = HistoryTransferAutoDataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
