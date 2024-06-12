from typing import Dict, List, Tuple, Union

from _decimal import Decimal
from django.db.models import Sum
from django.utils import timezone
from rest_framework.request import Request

from .serializers import IncomeStatisticViewSerializer, \
    CategoryViewSerializer, ExpensesViewSerializer, GoalTransferStatisticSerializer
from datetime import datetime, timedelta
from decimal import Decimal
import re

from drf_multiple_model.views import ObjectMultipleModelAPIView

from backend.apps.history.models import HistoryIncome, HistoryExpense, HistoryTransfer
from backend.apps.history.serializers import HistoryExpenseSerializer, \
    HistoryExpenseAutoDataSerializer, HistoryIncomeAutoDataSerializer, HistoryTransferAutoDataSerializer

from rest_framework import generics
from rest_framework.response import Response
from backend.apps.history.serializers import HistoryIncomeSerializer, CombinedStatisticSerializer
from backend.apps.account.permissions import IsSpaceMember
from backend.apps.space.models import Space

from backend.apps.account.models import Account
from backend.apps.category.models import Category
from backend.apps.goal.models import Goal


class HistoryView(ObjectMultipleModelAPIView):
    permission_classes = (IsSpaceMember,)

    def get_querylist(self):
        space_pk = self.kwargs["space_pk"]
        return [
            {"queryset": HistoryIncome.objects.filter(father_space_id=space_pk), "serializer_class":
                HistoryIncomeSerializer},
            {"queryset": HistoryExpense.objects.filter(father_space_id=space_pk), "serializer_class":
                HistoryExpenseSerializer}
        ]


class StatisticView(generics.GenericAPIView):
    permission_classes = (IsSpaceMember,)

    @staticmethod
    def get(request, *args, **kwargs):
        categories_view = CategoryStatisticView.as_view()(request._request, *args, **kwargs)
        incomes_view = IncomeStatisticView.as_view()(request._request, *args, **kwargs)
        expenses_view = ExpensesStatisticView.as_view()(request._request, *args, **kwargs)
        goal_view = GoalTransferStatisticView.as_view()(request._request, *args, **kwargs)
        balance_view = GeneralView.as_view()(request._request, *args, **kwargs)
        recurring_payments = RecurringPaymentsStatistic.as_view()(request._request, *args, **kwargs)

        combined_data = {
            "Expenses": expenses_view.data,
            "Balance": balance_view.data,
            "Incomes": incomes_view.data,
            "Goals": goal_view.data,
            "Recurring_Payments": recurring_payments.data,
            "Categories": categories_view.data,
        }

        serializer = CombinedStatisticSerializer(combined_data)
        return Response(serializer.data)


class CategoryStatisticView(generics.ListAPIView):
    permission_classes = (IsSpaceMember,)
    serializer_class = CategoryViewSerializer

    def get_queryset(self) -> Dict[str, List[HistoryExpense]]:
        queryset = HistoryExpense.objects.exclude(to_cat__isnull=True).filter(father_space=self.kwargs['space_pk'],
                                                                              periodic_expense=False)
        periods = [(7, "week"), (30, "month"), (90, "three_month"), (365, "year")]
        return {period: self.get_expenses_for_period(queryset, days) for days, period in periods}

    @staticmethod
    def get_expenses_for_period(queryset, days: int) -> List[HistoryExpense]:
        return queryset.filter(created__gte=datetime.now() - timedelta(days=days))

    def get_summary_and_percentages(self, expenses: List[HistoryExpense]) -> tuple[dict[str, Decimal], dict[str, int]]:
        expenses = [expense for expense in expenses if expense.to_cat]
        total = sum(expense.amount_in_default_currency for expense in expenses)
        summary = self.get_summary(expenses)
        percentages = self.get_percentages(summary, total)
        return summary, percentages

    @staticmethod
    def get_summary(expenses: List[HistoryExpense]) -> Dict[str, Decimal]:
        summary = {}
        for expense in expenses:
            if expense.to_cat:
                icon_name = expense.to_cat.icon
                amount = expense.amount_in_default_currency
                if icon_name in summary:
                    summary[icon_name] += amount
                else:
                    summary[icon_name] = amount
        return summary

    @staticmethod
    def get_percentages(summary: Dict[str, float], total: float) -> dict[str, str]:
        percentages = {category: round(value / total * 100) for category, value in summary.items()}
        remaining_percentage = 100 - sum(percentages.values())
        if remaining_percentage != 0:
            sorted_percentages = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
            if sorted_percentages:
                largest_category, _ = sorted_percentages[0]
                percentages[largest_category] += remaining_percentage
        return {category: f"{value}%" for category, value in percentages.items()}

    def add_currency(self, data: Union[Dict, Decimal], currency: str) -> Union[Dict, str]:
        if isinstance(data, Decimal):
            return f"{data} {currency}"
        else:
            return {
                key: f"{value} {currency}" if isinstance(value, (int, float, Decimal)) else self.add_currency(value,
                                                                                                              currency)
                for key, value in data.items()
            }

    def format_result(self, expenses: Dict[str, List[HistoryExpense]], request) -> Dict:
        formatted_result = {}
        for period, period_expenses in expenses.items():
            if not period_expenses:
                formatted_result[period.capitalize()] = {}
                formatted_result[f"{period.capitalize()}_Percent"] = {}
                formatted_result[
                    f"Analyze_{period.capitalize()}"] = f"You didn't make any category expenditures this {period}"
            else:
                space = Space.objects.get(pk=self.kwargs.get("space_pk"))
                summary, percentages = self.get_summary_and_percentages(period_expenses)
                formatted_result[period.capitalize()] = self.add_currency(summary, space.currency)
                formatted_result[f"{period.capitalize()}_Percent"] = percentages
                if summary:
                    max_spending_category = max(summary, key=summary.get)
                else:
                    max_spending_category = "No categories"
                formatted_result[
                    f"Analyze_{period.capitalize()}"] = f"This {period}, you spend most on {max_spending_category} category"
        return formatted_result

    def list(self, request, *args, **kwargs) -> Response:
        expenses = self.get_queryset()
        formatted_result = self.format_result(expenses, request)
        serializer = self.get_serializer(formatted_result, many=False)
        return Response(serializer.data)


class IncomeStatisticView(generics.ListAPIView):
    permission_classes = (IsSpaceMember,)
    serializer_class = IncomeStatisticViewSerializer

    def get_queryset(self) -> List[HistoryIncome]:
        return HistoryIncome.objects.filter(father_space=self.kwargs['space_pk'])

    @staticmethod
    def get_periods(incomes: List[HistoryIncome]) -> Dict[str, List[HistoryIncome]]:
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
            if days_since_creation < 365:
                periods['year'].append(income)
            if days_since_creation < 90:
                periods['three_month'].append(income)
            if days_since_creation < 30:
                periods['month'].append(income)
            if days_since_creation < 7:
                periods['week'].append(income)

        return periods

    @staticmethod
    def get_summary_and_percentages(incomes: List[HistoryIncome]) -> Tuple[Dict[str, float], Dict[str, int]]:
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
            sorted_percentages = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
            if sorted_percentages:
                largest_date, _ = sorted_percentages[0]
                percentages[largest_date] += remaining_percentage

        percentages = {date: f"{value}%" for date, value in percentages.items()}
        return summary, percentages

    def add_currency(self, data: Union[Dict, Decimal], currency: str) -> Union[Dict, str]:
        if isinstance(data, Decimal):
            return f"{data} {currency}"
        else:
            return {
                key: f"{value} {currency}" if isinstance(value, (int, float, Decimal)) else self.add_currency(value,
                                                                                                              currency)
                for key, value in data.items()
            }

    def format_result(self, incomes: List[HistoryIncome], request: Request) -> Dict:
        periods = self.get_periods(incomes)
        formatted_result = {}
        space = Space.objects.get(pk=self.kwargs.get("space_pk"))

        for period, period_incomes in periods.items():
            summary, percentages = self.get_summary_and_percentages(period_incomes)
            formatted_result[period.capitalize()] = self.add_currency(summary, space.currency)
            formatted_result[f"{period.capitalize()}_Percent"] = percentages

            if summary:
                max_income_date = max(summary, key=summary.get)
                max_income_value = summary[max_income_date]
                formatted_result[
                    f"Analyze_{period.capitalize()}"] = f"For this {period} the most {max_income_value} {space.currency} you earned on {max_income_date}"
            else:
                formatted_result[
                    f"Analyze_{period.capitalize()}"] = f"For this {period} you did not receive any income."

        return formatted_result

    def list(self, request: Request, *args, **kwargs) -> Response:
        incomes = self.get_queryset()
        formatted_result = self.format_result(incomes, request)
        return Response(formatted_result)


class ExpensesStatisticView(generics.ListAPIView):
    permission_classes = (IsSpaceMember,)
    serializer_class = ExpensesViewSerializer

    def get_queryset(self) -> List[HistoryExpense]:
        return HistoryExpense.objects.filter(father_space=self.kwargs['space_pk'])

    @staticmethod
    def get_periods(expenses: List[HistoryExpense]) -> Dict[str, List[HistoryExpense]]:
        now = timezone.now()
        week_ago = now - timezone.timedelta(days=7)
        month_ago = now - timezone.timedelta(days=30)
        three_month_ago = now - timezone.timedelta(days=90)
        year_ago = now - timezone.timedelta(days=365)
        periods = {
            'Week': [],
            'Month': [],
            'Three_month': [],
            'Year': [],
        }
        for expense in expenses:
            days_since_creation = (now - expense.created).days
            if days_since_creation < 365:
                periods['Year'].append(expense)
            if days_since_creation < 90:
                periods['Three_month'].append(expense)
            if days_since_creation < 30:
                periods['Month'].append(expense)
            if days_since_creation < 7:
                periods['Week'].append(expense)
        return periods

    @staticmethod
    def get_summary_and_percentages(expenses: List[HistoryExpense]) -> tuple[
        dict[str, int], dict[str, str] | dict[str, str]]:
        category_expenses = sum(expense.amount for expense in expenses if expense.to_cat)
        loss_expenses = sum(expense.amount for expense in expenses if not expense.to_cat)
        recurring_expenses = sum(expense.amount for expense in expenses if expense.periodic_expense)
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
        if not expenses:
            return f"You haven't made a single spending spree this {period}"
        _, percentages = self.get_summary_and_percentages(expenses)
        max_category = max(percentages, key=lambda x: percentages[x].rstrip('%'))
        return f"The most you've spent this {period} on {max_category}"

    def format_result(self, expenses: List[HistoryExpense], request: Request) -> Dict:
        periods = self.get_periods(expenses)
        currency = Space.objects.get(pk=self.kwargs.get("space_pk")).currency
        result = {}

        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        three_month_start = (today - timedelta(days=90)).replace(day=1)
        year_start = today.replace(month=1, day=1)

        for period, period_expenses in periods.items():
            if period == 'Week':
                start_date = week_start
            elif period == 'Month':
                start_date = month_start
            elif period == 'Three_month':
                start_date = three_month_start
            else:  # 'Year'
                start_date = year_start

            result[period] = {}
            result[f"{period}_Percent"] = {}

            if not period_expenses:
                result[period] = f"0 {currency}"
                result[f"{period}_Percent"] = "0 %"
            else:
                for expense in period_expenses:
                    date_str = expense.created.date().strftime("%Y-%m-%d")  # Changed to YYYY-MM-DD format
                    summary, percentages = self.get_summary_and_percentages([expense])
                    summary_with_currency = {key: f"{val} {currency}" for key, val in summary.items()}
                    result[period][date_str] = summary_with_currency
                    result[f"{period}_Percent"][date_str] = percentages

            result[f"Analyze_{period}"] = self.analyze_expenses(period_expenses, period)

        return result

    def list(self, request: Request, *args, **kwargs) -> Response:
        expenses = self.get_queryset()
        result = self.format_result(expenses, request)
        return Response(result)


class GoalTransferStatisticView(generics.ListAPIView):
    permission_classes = (IsSpaceMember,)
    serializer_class = GoalTransferStatisticSerializer

    def get_queryset(self) -> List[HistoryTransfer]:
        return HistoryTransfer.objects.exclude(to_goal__isnull=True) \
            .exclude(to_goal__exact=None) \
            .filter(father_space=self.kwargs['space_pk'])

    def get_periods(self, transfers: List[HistoryTransfer]) -> Dict[str, List[HistoryTransfer]]:
        periods = self._init_periods()

        for transfer in transfers:
            created = self._normalize_datetime(transfer.created)
            days_since_creation = self._days_since_creation(created)
            self._add_to_periods(periods, transfer, days_since_creation)

        return periods

    @staticmethod
    def _init_periods() -> Dict[str, List[HistoryTransfer]]:
        return {
            'Week': [],
            'Month': [],
            'Three_month': [],
            'Year': [],
        }

    @staticmethod
    def _normalize_datetime(dt: datetime) -> datetime:
        return dt.replace(tzinfo=None)

    @staticmethod
    def _days_since_creation(created: datetime) -> int:
        now = timezone.now().replace(tzinfo=None)
        return (now - created).days

    @staticmethod
    def _add_to_periods(periods: Dict[str, List[HistoryTransfer]], transfer: HistoryTransfer,
                        days_since_creation: int) -> None:
        if days_since_creation < 7:
            periods['Week'].append(transfer)
            periods['Month'].append(transfer)
            periods['Three_month'].append(transfer)
            periods['Year'].append(transfer)
        elif days_since_creation < 30:
            periods['Month'].append(transfer)
            periods['Three_month'].append(transfer)
            periods['Year'].append(transfer)
        elif days_since_creation < 90:
            periods['Three_month'].append(transfer)
            periods['Year'].append(transfer)
        else:
            periods['Year'].append(transfer)

    def get_summary(self, transfers: List[HistoryTransfer], currency: str) -> Dict[str, Dict[str, str]]:
        summary = {}
        for transfer in transfers:
            self._update_summary(summary, transfer, currency)
        sorted_summary = dict(
            sorted(summary.items(), key=lambda x: Decimal(x[1]['Collected'].split()[0]), reverse=True)[:5])
        return sorted_summary

    def _update_summary(self, summary: Dict[str, Dict[str, str]], transfer: HistoryTransfer, currency: str) -> None:
        goal = transfer.to_goal.title
        goal_amount = transfer.goal_amount
        collected = transfer.amount_in_default_currency

        if goal not in summary:
            summary[goal] = {
                "Goal_amount": f"{goal_amount} {currency}" if goal_amount else "",
                "Collected": f"{collected} {currency}" if collected else "",
            }
        else:
            existing_collected = Decimal(summary[goal]['Collected'].split()[0])
            summary[goal]['Collected'] = f"{existing_collected + collected} {currency}"

    def get_percentages(self, transfers: List[HistoryTransfer]) -> Dict[str, Dict[str, str]]:
        goal_amounts = self._init_goal_amounts(transfers)
        percentages = self._calculate_percentages(goal_amounts)
        return percentages

    @staticmethod
    def _init_goal_amounts(transfers: List[HistoryTransfer]) -> Dict[str, Dict[str, Decimal]]:
        goal_amounts = {}
        for transfer in transfers:
            goal = transfer.to_goal.title
            goal_amount = transfer.goal_amount
            collected = transfer.amount_in_default_currency

            goal_amounts.setdefault(goal, {'Goal_amount': goal_amount, 'Collected': Decimal('0')})
            goal_amounts[goal]['Collected'] += collected

        return goal_amounts

    @staticmethod
    def _calculate_percentages(goal_amounts: Dict[str, Dict[str, Decimal]]) -> Dict[str, Dict[str, str]]:
        percentages = {}
        for goal, goal_data in goal_amounts.items():
            goal_amount = goal_data['Goal_amount']
            collected = goal_data['Collected']

            if goal_amount:
                collected_percentage = round(collected / goal_amount * 100)
            else:
                collected_percentage = 100

            percentages[goal] = {
                "Collected": f"{collected_percentage}%",
            }

        return percentages

    def analyze(self, summary: Dict[str, Dict[str, str]], currency: str) -> str:
        goal_diffs = self._get_goal_diffs(summary, currency)
        if goal_diffs:
            closest_goal, smallest_diff = min(goal_diffs.items(), key=lambda x: x[1])
            rounded_diff = int(round(smallest_diff))
            return f"You are closest to accumulating on goal {closest_goal}, you have {rounded_diff} {currency} to go."
        else:
            return f"You haven't spent any money on goals."

    def _get_goal_diffs(self, summary: Dict[str, Dict[str, str]], currency: str) -> Dict[str, Decimal]:
        goal_diffs = {}
        for goal, data in summary.items():
            goal_amount = data['Goal_amount'].split()[0] if data['Goal_amount'] else None
            collected = data['Collected'].split()[0] if data['Collected'] else None
            if goal_amount and collected:
                goal_amount = Decimal(goal_amount)
                collected = Decimal(collected)
                diff = abs(goal_amount - collected)
                goal_diffs[goal] = diff
        return goal_diffs

    def list(self, request, *args, **kwargs):
        transfers = self.get_queryset()
        periods = self.get_periods(transfers)
        currency = Space.objects.get(pk=self.kwargs.get("space_pk")).currency
        result = {}

        for period, period_transfers in periods.items():
            summary = self.get_summary(period_transfers, currency)
            percentages = self.get_percentages(period_transfers)
            result[period] = summary
            result[f"{period}_Percent"] = percentages
            analysis_message = self.analyze(summary, currency)
            result[f"Analyze_{period}"] = analysis_message

        serializer = self.get_serializer(result)
        return Response(serializer.data)


class GeneralView(generics.GenericAPIView):
    permission_classes = (IsSpaceMember,)

    def get(self, request, space_pk, *args, **kwargs):
        data = {}
        data["Week"], data["Week_Percent"], data["Analyze_Week"] = self.get_data_and_analysis(7, space_pk)
        data["Month"], data["Month_Percent"], data["Analyze_Month"] = self.get_data_and_analysis(30, space_pk)
        data["Three_month"], data["Three_month_Percent"], data["Analyze_Three_month"] = self.get_data_and_analysis(90,
                                                                                                                   space_pk)
        data["Year"], data["Year_Percent"], data["Analyze_Year"] = self.get_data_and_analysis(365, space_pk)
        return Response(data)

    def get_data_and_analysis(self, days, space_pk):
        period_data = self.get_data_for_period(days, space_pk)
        analysis = self.get_analysis(days, space_pk, period_data)
        percentages = self.get_percentages(period_data)
        return period_data, percentages, analysis

    def get_data_for_period(self, days, space_pk):
        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()
        expenses = HistoryExpense.objects.filter(
            created__range=[start_date, end_date],
            father_space_id=space_pk
        ).values('created').annotate(
            expenses=Sum('amount_in_default_currency')
        ).order_by('created')
        incomes = HistoryIncome.objects.filter(
            created__range=[start_date, end_date],
            father_space_id=space_pk
        ).values('created').annotate(
            incomes=Sum('amount_in_default_currency')
        ).order_by('created')
        transfers = HistoryTransfer.objects.filter(
            created__range=[start_date, end_date],
            father_space_id=space_pk,
            goal_is_done=True
        ).values('created').annotate(
            expenses=Sum('amount_in_default_currency')
        ).order_by('created')

        period_data = {}
        initial_balance = self.get_initial_balance(start_date, space_pk)

        for expense in expenses:
            date_str = expense['created'].strftime('%Y-%m-%d')
            income = next((inc for inc in incomes if inc['created'].date() == expense['created'].date()),
                          {'incomes': 0})
            transfer = next((tr for tr in transfers if tr['created'].date() == expense['created'].date()),
                            {'expenses': 0})
            balance = initial_balance + income['incomes'] - (expense['expenses'] + transfer['expenses'])
            period_data[date_str] = self.format_balance(balance, initial_balance, space_pk)

        for income in incomes:
            date_str = income['created'].strftime('%Y-%m-%d')
            if date_str not in period_data:
                balance = initial_balance + income['incomes']
                period_data[date_str] = self.format_balance(balance, initial_balance, space_pk)

        return period_data

    @staticmethod
    def get_initial_balance(start_date, space_pk):
        expenses = HistoryExpense.objects.filter(created__lt=start_date, father_space_id=space_pk).aggregate(
            Sum('amount_in_default_currency'))['amount_in_default_currency__sum'] or Decimal(0)
        incomes = HistoryIncome.objects.filter(created__lt=start_date, father_space_id=space_pk).aggregate(
            Sum('amount_in_default_currency'))['amount_in_default_currency__sum'] or Decimal(0)
        transfers = \
        HistoryTransfer.objects.filter(created__lt=start_date, father_space_id=space_pk, goal_is_done=True).aggregate(
            Sum('amount_in_default_currency'))['amount_in_default_currency__sum'] or Decimal(0)
        return incomes - (expenses + transfers)

    def format_balance(self, balance, initial_balance, space_pk):
        percentage = round((balance / initial_balance) * 100, 2) if initial_balance != 0 else 0
        return {'balance': f"{balance} {self.get_currency(space_pk)}", 'percentage': f"{percentage}%"}

    def get_analysis(self, days, space_pk, period_data):
        if not period_data:
            return "No data available for this period."

        start_percentage = float(next(iter(period_data.values()))['percentage'].strip('%'))
        end_percentage = float(next(reversed(period_data.values()))['percentage'].strip('%'))
        change = end_percentage - start_percentage
        return f"Your balance changed by {change}% over the last {days} days."

    def get_percentages(self, period_data):
        return {date: data['percentage'] for date, data in period_data.items()}

    def get_currency(self, space_pk):
        return Space.objects.get(pk=space_pk).currency

    def format_amount(self, amount, space_pk):
        rounded_amount = round(float(re.sub(r'[^\d.]', '', str(amount))))
        currency = self.get_currency(space_pk)
        return f"{rounded_amount} {currency}"


class RecurringPaymentsStatistic(generics.ListAPIView):
    permission_classes = (IsSpaceMember,)
    serializer_class = CategoryViewSerializer

    def get_queryset(self) -> Dict[str, List[HistoryExpense]]:
        queryset = HistoryExpense.objects.exclude(to_cat__isnull=True).filter(father_space=self.kwargs['space_pk'],
                                                                              periodic_expense=True)
        periods = [(7, "week"), (30, "month"), (90, "three_month"), (365, "year")]
        return {period: self.get_expenses_for_period(queryset, days) for days, period in periods}

    @staticmethod
    def get_expenses_for_period(queryset, days: int) -> List[HistoryExpense]:
        return queryset.filter(created__gte=timezone.now() - timedelta(days=days))

    def get_summary_and_percentages(self, expenses: List[HistoryExpense]) -> Tuple[Dict[str, float], Dict[str, int]]:
        expenses = [expense for expense in expenses if expense.to_cat]
        total = sum(expense.amount_in_default_currency for expense in expenses)
        summary = self.get_summary(expenses)
        percentages = self.get_percentages(summary, total)
        return summary, percentages

    @staticmethod
    def get_summary(expenses: List[HistoryExpense]) -> Dict[str, float]:
        summary = {
            expense.to_cat.title: sum(
                expense.amount_in_default_currency for expense in expenses if expense.to_cat == category)
            for expense in expenses for category in {expense.to_cat}
        }
        return dict(sorted(summary.items(), key=lambda x: x[1], reverse=True)[:5])

    @staticmethod
    def get_percentages(summary: Dict[str, float], total: float) -> Dict[str, int]:
        percentages = {category: round(value / total * 100) for category, value in summary.items()}
        remaining_percentage = 100 - sum(percentages.values())
        if remaining_percentage != 0:
            sorted_percentages = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
            for category, _ in sorted_percentages[5:]:
                del percentages[category]
            if sorted_percentages:
                largest_category, _ = sorted_percentages[0]
                percentages[largest_category] += remaining_percentage
        return {category: f"{value}%" for category, value in percentages.items()}

    def add_currency(self, data: Union[Dict, Decimal], currency: str) -> Union[Dict, str]:
        if isinstance(data, Decimal):
            return f"{int(data)} {currency}"
        else:
            return {key: f"{int(value)} {currency}" if isinstance(value, (int, float, Decimal)) else self.add_currency(
                value, currency) for key, value in data.items()}

    def format_result(self, expenses: Dict[str, List[HistoryExpense]], request: Request) -> Dict:
        formatted_result = {}
        currency = Space.objects.get(pk=self.kwargs.get("space_pk")).currency
        for period, period_expenses in expenses.items():
            summary, percentages = self.get_summary_and_percentages(period_expenses)
            period_sum = sum(summary.values())
            formatted_result[period.capitalize()] = self.add_currency(summary, currency)
            formatted_result[f"{period.capitalize()}_Percent"] = self.get_percentage_for_summary(summary, period_sum)
            formatted_result[f"Analyze_{period.capitalize()}"] = self.get_analysis_message(summary, currency, period)
        return formatted_result

    @staticmethod
    def get_percentage_for_summary(summary: Dict[str, float], period_sum: float) -> Dict[str, str]:
        return {category: f"{round(value / period_sum * 100)}%" for category, value in summary.items()}

    def get_analysis_message(self, summary: Dict[str, float], currency: str, period: str) -> str:
        if summary:
            max_spending_category = max(summary, key=summary.get)
            max_spending_amount = summary[max_spending_category]
            return f"This {period}, your biggest recurring expense {max_spending_category}, you have spent {self.add_currency(max_spending_amount, currency)}"
        else:
            return f"You did not have any recurring expenses this {period}."

    def list(self, request: Request, *args, **kwargs) -> Response:
        expenses = self.get_queryset()
        formatted_result = self.format_result(expenses, request)
        serializer = self.get_serializer(formatted_result, many=False)
        return Response(serializer.data)


class StatisticSimulation(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        incomes_view = IncomeAutoDataView.as_view()(request._request, *args, **kwargs)
        expenses_view = ExpenseAutoDataView.as_view()(request._request, *args, **kwargs)
        transfer_view = TransferAutoDataView.as_view()(request._request, *args, **kwargs)
        combined_data = {
            "Incomes is ready": incomes_view.data,
            "Spending is ready": expenses_view.data,
            "Goals is ready": transfer_view.data,
        }
        return Response(combined_data)


class IncomeAutoDataView(generics.ListAPIView):
    permission_classes = ()
    serializer_class = HistoryIncomeAutoDataSerializer

    def get_queryset(self):
        father_space_id = self.kwargs["space_pk"]
        father_space = Space.objects.get(id=father_space_id)
        account = Account.objects.create(title='Cash', balance=1000, currency='USD', father_space=father_space)
        income_data = [
            {'amount': 1500, 'amount_in_default_currency': 1500, 'father_space': father_space, 'currency': 'USD',
             'account': account, 'created': datetime(2023, 1, 1), 'comment': ''},
            {'amount': 100, 'amount_in_default_currency': 100, 'father_space': father_space, 'currency': 'USD',
             'account': account, 'created': datetime(2023, 3, 1), 'comment': ''},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'account': account, 'created': datetime(2023, 5, 1), 'comment': ''},
            {'amount': 1500, 'amount_in_default_currency': 1500, 'father_space': father_space, 'currency': 'USD',
             'account': account, 'created': datetime(2023, 9, 1), 'comment': ''},
            {'amount': 50, 'amount_in_default_currency': 50, 'father_space': father_space, 'currency': 'USD',
             'account': account, 'created': datetime(2023, 11, 1), 'comment': ''},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': account, 'created': datetime(2023, 12, 1), 'comment': ''},
            {'amount': 1900, 'amount_in_default_currency': 1900, 'father_space': father_space, 'currency': 'USD',
             'account': account, 'created': datetime(2023, 12, 15), 'comment': ''},
            {'amount': 500, 'amount_in_default_currency': 500, 'father_space': father_space, 'currency': 'USD',
             'account': account, 'created': datetime(2023, 12, 30), 'comment': ''},
            {'amount': 390, 'amount_in_default_currency': 390, 'father_space': father_space, 'currency': 'USD',
             'account': account, 'created': datetime(2024, 3, 5), 'comment': ''},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': account, 'created': datetime(2024, 4, 10), 'comment': ''},
            {'amount': 2000, 'amount_in_default_currency': 2000, 'father_space': father_space, 'currency': 'USD',
             'account': account, 'created': datetime(2024, 4, 19), 'comment': ''},
            {'amount': 300, 'amount_in_default_currency': 300, 'father_space': father_space, 'currency': 'USD',
             'account': account, 'created': datetime(2024, 4, 20), 'comment': ''},
            {'amount': 900, 'amount_in_default_currency': 900, 'father_space': father_space, 'currency': 'USD',
             'account': account, 'created': datetime(2024, 4, 22), 'comment': ''},
            {'amount': 10000, 'amount_in_default_currency': 10000, 'father_space': father_space, 'currency': 'USD',
             'account': account, 'created': datetime(2024, 4, 24), 'comment': ''},
            {'amount': 1000, 'amount_in_default_currency': 100, 'father_space': father_space, 'currency': 'USD',
             'account': account, 'created': datetime(2024, 4, 25), 'comment': ''}
        ]

        incomes = [HistoryIncome(**data) for data in income_data]
        HistoryIncome.objects.bulk_create(incomes)
        return HistoryIncome.objects.filter(father_space=father_space)


class ExpenseAutoDataView(generics.ListAPIView):
    permission_classes = ()
    serializer_class = HistoryExpenseAutoDataSerializer

    def get_queryset(self):
        father_space_id = self.kwargs["space_pk"]
        father_space = Space.objects.get(id=father_space_id)
        account = Account.objects.create(title='Cash', balance=1000, currency='USD', father_space=father_space)
        category_names = [
            'Food',
            'Home',
            'Utilities',
            'Subscription',
            'Insurance',
            'Transportation',
            'Entertainment',
            'Health',
            'Gifts',
            'Education',
            'Rent',
            'Maintenance',
            'Sports',
            'Parking',
            'Park'
        ]
        categories = {name: Category.objects.create(title=name, spent=100, limit=10000,
                                                    color='#a3e12f',
                                                    icon='FORWARD', father_space=father_space)
                      for name in category_names}
        expense_data = [
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account, 'created': datetime(2023, 1, 30),
             'comment': '', 'to_cat': categories['Food'], 'cat_icon': 'Donut'},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2023, 3, 20), 'comment': '', 'to_cat': categories['Home'],
             'cat_icon': 'Home'},
            {'amount': 2000, 'amount_in_default_currency': 2000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2023, 5, 11), 'comment': '', 'to_cat': categories['Food'],
             'cat_icon': 'Donut'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account, 'created': datetime(2023, 9, 11),
             'comment': '', 'to_cat': categories['Food'], 'cat_icon': 'Donut'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2024, 3, 10), 'comment': '', 'to_cat': categories['Home'],
             'cat_icon': 'Home'},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2024, 2, 2), 'comment': '', 'to_cat': categories['Food'],
             'cat_icon': 'Donut'},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2024, 2, 16), 'comment': '', 'to_cat': categories['Food'],
             'cat_icon': 'Donut'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2024, 1, 31), 'comment': '', 'to_cat': categories['Home'],
             'cat_icon': 'Home'},
            {'amount': 100, 'amount_in_default_currency': 100, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2024, 3, 6), 'comment': '', 'to_cat': categories['Food'],
             'cat_icon': 'Donut'},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2024, 4, 2), 'comment': '', 'to_cat': categories['Home'],
             'cat_icon': 'Home'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account, 'created': datetime(2024, 5, 3),
             'comment': '', 'to_cat': categories['Food'], 'cat_icon': 'Donut'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account, 'created': datetime(2024, 5, 3),
             'comment': '', 'to_cat': categories['Utilities'], 'cat_icon': 'Bolt'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account, 'created': datetime(2024, 5, 3),
             'comment': '', 'to_cat': categories['Subscription'], 'cat_icon': 'Film'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account, 'created': datetime(2024, 5, 3),
             'comment': '', 'to_cat': categories['Insurance'], 'cat_icon': 'Shield'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account, 'created': datetime(2024, 5, 3),
             'comment': '', 'to_cat': categories['Transportation'], 'cat_icon': 'Cart'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2024, 5, 4), 'comment': '', 'to_cat': categories['Food'],
             'cat_icon': 'Donut'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2024, 5, 5), 'comment': '', 'to_cat': categories['Home'],
             'cat_icon': 'Home'},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2024, 5, 6), 'comment': '', 'to_cat': categories['Food'],
             'cat_icon': 'Donut'},
            {'amount': 2000, 'amount_in_default_currency': 2000, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account, 'created': datetime(2024, 5, 8), 'comment': '',
             'to_cat': categories['Home']},
            {'amount': 50, 'amount_in_default_currency': 50, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2024, 5, 15), 'comment': '',
             'to_cat': categories['Entertainment'],
             'cat_icon': 'Camera'},
            {'amount': 75, 'amount_in_default_currency': 75, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2024, 5, 16), 'comment': '',
             'to_cat': categories['Transportation'],
             'cat_icon': 'Cart'},
            {'amount': 120, 'amount_in_default_currency': 120, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2024, 5, 17), 'comment': '', 'to_cat': categories['Health'],
             'cat_icon': 'Pill'},
            {'amount': 200, 'amount_in_default_currency': 200, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2024, 5, 18), 'comment': '', 'to_cat': categories['Gifts'],
             'cat_icon': 'Gift'},
            {'amount': 80, 'amount_in_default_currency': 80, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2024, 5, 19), 'comment': '', 'to_cat': categories['Education'],
             'cat_icon': 'Book'},
            {'amount': 300, 'amount_in_default_currency': 300, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2024, 5, 20), 'comment': '',
             'to_cat': categories['Entertainment'], 'cat_icon': 'Camera'},
            {'amount': 120, 'amount_in_default_currency': 120, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2024, 5, 21), 'comment': '', 'to_cat': categories['Gifts'],
             'cat_icon': 'Gift'},
            {'amount': 60, 'amount_in_default_currency': 60, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'created': datetime(2024, 5, 22), 'comment': '',
             'to_cat': categories['Transportation'],
             'cat_icon': 'Cart'},
            {'amount': 25, 'amount_in_default_currency': 25, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account, 'created': datetime(2024, 5, 13),
             'comment': 'Еженедельная подписка', 'to_cat': categories['Subscription'], 'cat_icon': 'Camera'},
            {'amount': 100, 'amount_in_default_currency': 100, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account, 'created': datetime(2023, 10, 1),
             'comment': 'Годовая страховка авто', 'to_cat': categories['Insurance'], 'cat_icon': 'Shield'},
            {'amount': 80, 'amount_in_default_currency': 80, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account, 'created': datetime(2024, 3, 15),
             'comment': 'Квартальная арендная плата', 'to_cat': categories['Rent'], 'cat_icon': 'Home'},
            {'amount': 300, 'amount_in_default_currency': 300, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account, 'created': datetime(2024, 5, 1),
             'comment': 'Полугодовая плата за обучение', 'to_cat': categories['Education'], 'cat_icon': 'Book'},
            {'amount': 40, 'amount_in_default_currency': 40, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account, 'created': datetime(2024, 5, 11),
             'comment': 'Еженедельные расходы на транспорт', 'to_cat': categories['Transportation'],
             'cat_icon': 'Cart'},
            {'amount': 1500, 'amount_in_default_currency': 1500, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account, 'created': datetime(2024, 3, 15),
             'comment': 'Годовая плата за обслуживание', 'to_cat': categories['Maintenance'], 'cat_icon': 'Waterdrop'},
            {'amount': 60, 'amount_in_default_currency': 60, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account, 'created': datetime(2024, 5, 15),
             'comment': 'Ежемесячная плата за фитнес', 'to_cat': categories['Sports'], 'cat_icon': 'Running'},
            {'amount': 200, 'amount_in_default_currency': 200, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account, 'created': datetime(2024, 4, 1),
             'comment': 'Квартальная оплата интернета', 'to_cat': categories['Utilities'], 'cat_icon': 'Home_WiFi'},
            {'amount': 125, 'amount_in_default_currency': 125, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account, 'created': datetime(2024, 5, 24),
             'comment': 'Ежегодный платеж за парковку', 'to_cat': categories['Parking'], 'cat_icon': 'Stop'},
            {'amount': 3464, 'amount_in_default_currency': 3464, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account, 'created': datetime(2024, 5, 24),
             'comment': 'Ежегодный платеж за парковку', 'to_cat': categories['Park'], 'cat_icon': 'Stop'}
        ]
        expenses = [HistoryExpense(**data) for data in expense_data]
        HistoryExpense.objects.bulk_create(expenses)
        return HistoryExpense.objects.filter(father_space=father_space)


class TransferAutoDataView(generics.ListAPIView):
    permission_classes = ()
    serializer_class = HistoryTransferAutoDataSerializer

    def get_queryset(self):
        father_space_pk = self.kwargs["space_pk"]
        father_space = Space.objects.get(id=father_space_pk)

        goal_main1 = Goal.objects.create(title='main', goal=4000, collected=0, father_space=father_space)
        goal_main2 = Goal.objects.create(title='main2', goal=3000, collected=0, father_space=father_space)

        account = Account.objects.create(title='Cash', balance=1000, currency='USD', father_space=father_space)

        transfer_data = [
            {'amount': 100, 'amount_in_default_currency': 100, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2024, 5, 22), 'to_goal': goal_main1,
             'from_goal': goal_main2, 'goal_amount': 4000},
            {'amount': 150, 'amount_in_default_currency': 150, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2024, 5, 23), 'to_goal': goal_main1,
             'from_goal': goal_main2, 'goal_amount': 4000},
            {'amount': 200, 'amount_in_default_currency': 200, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2024, 5, 24), 'to_goal': goal_main2,
             'from_goal': goal_main1, 'goal_amount': 3000},
            {'amount': 250, 'amount_in_default_currency': 250, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2024, 5, 25), 'to_goal': goal_main2,
             'from_goal': goal_main1, 'goal_amount': 3000},
            {'amount': 300, 'amount_in_default_currency': 300, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2024, 5, 26), 'to_goal': goal_main2,
             'from_goal': goal_main1, 'goal_amount': 3000},
            {'amount': 400, 'amount_in_default_currency': 400, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2024, 5, 1), 'to_goal': goal_main1,
             'from_goal': goal_main2, 'goal_amount': 4000},
            {'amount': 500, 'amount_in_default_currency': 500, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2024, 5, 8), 'to_goal': goal_main1,
             'from_goal': goal_main2, 'goal_amount': 4000},
            {'amount': 600, 'amount_in_default_currency': 600, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2024, 5, 15), 'to_goal': goal_main2,
             'from_goal': goal_main1, 'goal_amount': 3000},
            {'amount': 700, 'amount_in_default_currency': 700, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2024, 5, 22), 'to_goal': goal_main2,
             'from_goal': goal_main1, 'goal_amount': 3000},
            {'amount': 800, 'amount_in_default_currency': 800, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2024, 5, 29), 'to_goal': goal_main2,
             'from_goal': goal_main1, 'goal_amount': 3000},
            {'amount': 900, 'amount_in_default_currency': 900, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2024, 4, 1), 'to_goal': goal_main1,
             'from_goal': goal_main2, 'goal_amount': 4000},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2024, 4, 15), 'to_goal': goal_main1,
             'from_goal': goal_main2, 'goal_amount': 4000},
            {'amount': 1100, 'amount_in_default_currency': 1100, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2024, 4, 22), 'to_goal': goal_main2,
             'from_goal': goal_main1, 'goal_amount': 3000},
            {'amount': 1200, 'amount_in_default_currency': 1200, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2024, 5, 1), 'to_goal': goal_main2,
             'from_goal': goal_main1, 'goal_amount': 3000},
            {'amount': 1300, 'amount_in_default_currency': 1300, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2024, 5, 15), 'to_goal': goal_main2,
             'from_goal': goal_main1, 'goal_amount': 3000},
            {'amount': 1400, 'amount_in_default_currency': 1400, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2023, 6, 1), 'to_goal': goal_main1,
             'from_goal': goal_main2, 'goal_amount': 4000},
            {'amount': 1500, 'amount_in_default_currency': 1500, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2023, 7, 1), 'to_goal': goal_main1,
             'from_goal': goal_main2, 'goal_amount': 4000},
            {'amount': 1600, 'amount_in_default_currency': 1600, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2023, 8, 1), 'to_goal': goal_main2,
             'from_goal': goal_main1, 'goal_amount': 3000},
            {'amount': 1700, 'amount_in_default_currency': 1700, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2023, 9, 1), 'to_goal': goal_main2,
             'from_goal': goal_main1, 'goal_amount': 3000},
            {'amount': 1800, 'amount_in_default_currency': 1800, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account, 'to_acc': account, 'created': datetime(2023, 10, 1), 'to_goal': goal_main2,
             'from_goal': goal_main1, 'goal_amount': 3000},
        ]
        transfers = [HistoryTransfer(**data) for data in transfer_data]
        HistoryTransfer.objects.bulk_create(transfers)

        return HistoryTransfer.objects.filter(father_space=father_space)
