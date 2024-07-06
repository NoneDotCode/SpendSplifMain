from typing import Dict, List, Tuple, Union

from django.db import transaction
from _decimal import Decimal
from django.utils import timezone
from rest_framework.request import Request
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

from .permissions import CanEditHistory, CanDeleteHistory
from .serializers import IncomeStatisticViewSerializer, \
    CategoryViewSerializer, ExpensesViewSerializer, GoalTransferStatisticSerializer, \
    HistoryExpenseEditSerializer, HistoryIncomeEditSerializer
from datetime import datetime, timedelta
from decimal import Decimal


from backend.apps.history.models import HistoryIncome, HistoryExpense, HistoryTransfer
from backend.apps.history.serializers import (HistoryExpenseAutoDataSerializer, HistoryIncomeAutoDataSerializer,
                                              HistoryTransferAutoDataSerializer)

from rest_framework import generics
from backend.apps.history.serializers import CombinedStatisticSerializer
from backend.apps.account.permissions import IsSpaceMember, IsSpaceOwner
from backend.apps.space.models import Space

from backend.apps.account.models import Account
from backend.apps.category.models import Category
from backend.apps.goal.models import Goal

from django.utils.timezone import make_aware, is_naive
import pytz


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from backend.apps.converter.utils import convert_number_to_letter, convert_currencies
from ..total_balance.models import TotalBalance


class HistoryView(APIView):
    permission_classes = [IsAuthenticated, IsSpaceMember]

    def post(self, request, space_pk):
        # Получаем временную зону, установленную middleware
        user_timezone = timezone.get_current_timezone()

        # Получаем лимит из тела JSON-запроса, по умолчанию возвращаем все записи
        limit = request.data.get('limit')
        try:
            limit = int(limit) if limit else None
        except ValueError:
            return Response({"error": "Invalid limit value"}, status=400)

        income_queryset = HistoryIncome.objects.filter(father_space_id=space_pk).order_by('-created')
        expense_queryset = HistoryExpense.objects.filter(father_space_id=space_pk).order_by('-created')

        combined_queryset = sorted(
            list(income_queryset) + list(expense_queryset),
            key=lambda x: x.created,
            reverse=True
        )

        # Применяем лимит, если он указан
        if limit is not None:
            combined_queryset = combined_queryset[:limit]

        serialized_data = []
        for item in combined_queryset:
            # Переводим время в пользовательскую временную зону
            localized_time = item.created.astimezone(user_timezone)
            formatted_date = localized_time.strftime('%Y-%m-%d')
            formatted_time = localized_time.strftime('%H:%M')

            if isinstance(item, HistoryIncome):
                serialized_data.append({
                    "id": item.id,
                    "type": "income",
                    "amount": item.amount,
                    "currency": item.currency,
                    "comment": item.comment,
                    "account": item.account["title"],
                    "account_balance": convert_number_to_letter(item.account["balance"]),
                    "created_date": formatted_date,
                    "created_time": formatted_time,
                })
            elif isinstance(item, HistoryExpense):
                try:
                    cat_title, cat_icon, history_type = item.to_cat["title"], item.to_cat["icon"], "expense"
                except TypeError:
                    cat_title, cat_icon, history_type = "", "", "loss"
                serialized_data.append({
                    "id": item.id,
                    "type": history_type,
                    "amount": item.amount,
                    "currency": item.currency,
                    "comment": item.comment,
                    "account": item.from_acc["title"],
                    "account_balance": convert_number_to_letter(item.from_acc["balance"]),
                    "category_title": cat_title,
                    "category_icon": cat_icon,
                    "periodic_expense": item.periodic_expense,
                    "created_date": formatted_date,
                    "created_time": formatted_time,
                })

        return Response(serialized_data)

    # Оставляем метод get для обратной совместимости
    def get(self, request, space_pk):
        return self.post(request, space_pk)


class HistoryExpenseEditView(APIView):
    permission_classes = (IsSpaceMember & (IsSpaceOwner | CanEditHistory),)

    @transaction.atomic
    def put(self, request, pk, *args, **kwargs):
        try:
            expense = HistoryExpense.objects.select_for_update().get(pk=pk)
        except HistoryExpense.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if timezone.now() - expense.created > timedelta(days=14):
            return Response({"error": "Cannot edit expenses older than 14 days"},
                            status=status.HTTP_403_FORBIDDEN)

        old_amount = expense.amount
        old_account_id = expense.from_acc["id"]
        old_category_id = expense.to_cat["id"] if expense.to_cat else None

        serializer = HistoryExpenseEditSerializer(data=request.data, partial=True)

        if serializer.is_valid():
            # Обновляем только переданные поля
            if 'amount' in request.data:
                new_amount = Decimal(request.data['amount'])
                expense.amount = new_amount
            else:
                new_amount = old_amount

            if 'account' in request.data:
                new_account_id = request.data['account']
            else:
                new_account_id = old_account_id

            if 'category' in request.data:
                new_category_id = request.data['category']
            else:
                new_category_id = old_category_id

            if 'comment' in request.data:
                expense.comment = request.data['comment']

            # Обновляем баланс счетов только если они существуют и изменились
            if old_account_id != new_account_id or old_amount != new_amount:
                try:
                    old_account = Account.objects.get(pk=old_account_id)
                    old_account.balance += old_amount
                    old_account.save()
                except ObjectDoesNotExist:
                    pass  # Старый счет не существует, пропускаем обновление

                try:
                    new_account = Account.objects.get(pk=new_account_id)
                    new_account.balance -= new_amount
                    new_account.save()
                    expense.from_acc = {
                        'id': new_account.id,
                        'title': new_account.title,
                        'balance': float(new_account.balance),
                        'currency': new_account.currency,
                        'included_in_total_balance': new_account.included_in_total_balance,
                        'father_space': new_account.father_space.id
                    }
                except ObjectDoesNotExist:
                    return Response({"error": "Specified new account does not exist"},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                new_account = expense.from_acc

            # Обновляем категории только если они существуют и изменились
            if old_category_id != new_category_id or old_amount != new_amount:
                if old_category_id:
                    try:
                        old_category = Category.objects.get(pk=old_category_id)
                        old_category.spent -= old_amount
                        old_category.save()
                    except ObjectDoesNotExist:
                        pass  # Старая категория не существует, пропускаем обновление

                if new_category_id:
                    try:
                        new_category = Category.objects.get(pk=new_category_id)
                        new_category.spent += new_amount
                        new_category.save()
                        expense.to_cat = {
                            'id': new_category.id,
                            'title': new_category.title,
                            'spent': float(new_category.spent),
                            'limit': float(new_category.limit) if new_category.limit else None,
                            'color': new_category.color,
                            'icon': new_category.icon,
                            'father_space': new_category.father_space.id
                        }
                    except ObjectDoesNotExist:
                        return Response({"error": "Specified new category does not exist"},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    expense.to_cat = None

            # Обновляем общий баланс пространства
            space = Space.objects.select_for_update().get(pk=expense.father_space_id)
            space.totalbalance.balance += old_amount - new_amount
            space.totalbalance.save()

            # Обновляем amount_in_default_currency
            expense.amount_in_default_currency = convert_currencies(
                amount=float(new_amount),
                from_currency=new_account['currency'],
                to_currency=space.currency
            )

            # Обновляем new_balance
            expense.new_balance = space.totalbalance.balance

            # Сохраняем изменения в расходе
            expense.save()

            return Response({"message": "Expense has been updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    patch = put

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        permission = CanDeleteHistory()
        if not permission.has_permission(request, self):
            return Response({"error": "You don't have permission to delete this history record"},
                            status=status.HTTP_403_FORBIDDEN)
        try:
            expense = HistoryExpense.objects.select_for_update().get(pk=pk)
        except HistoryExpense.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Проверяем, прошло ли больше 14 дней с момента создания записи
        if timezone.now() - expense.created > timedelta(days=14):
            return Response({"error": "Cannot delete expenses older than 14 days"},
                            status=status.HTTP_403_FORBIDDEN)

        old_amount = expense.amount
        old_account_id = expense.from_acc["id"]
        old_category_id = expense.to_cat["id"] if expense.to_cat else None

        # Возвращаем средства на счет
        try:
            account = Account.objects.get(pk=old_account_id)
            account.balance += old_amount
            account.save()
        except ObjectDoesNotExist:
            pass  # Счет не существует, пропускаем обновление

        # Уменьшаем потраченную сумму в категории
        if old_category_id:
            try:
                category = Category.objects.get(pk=old_category_id)
                category.spent -= old_amount
                category.save()
            except ObjectDoesNotExist:
                pass  # Категория не существует, пропускаем обновление

        # Обновляем общий баланс пространства
        space = Space.objects.select_for_update().get(pk=expense.father_space_id)
        space.totalbalance.balance += old_amount
        space.totalbalance.save()

        # Удаляем запись о расходе
        expense.delete()

        return Response({"message": "Expense has been deleted successfully"}, status=status.HTTP_200_OK)


class HistoryIncomeEditView(APIView):
    permission_classes = (IsSpaceMember & (IsSpaceOwner | CanEditHistory),)

    @transaction.atomic
    def put(self, request, pk, *args, **kwargs):
        try:
            income = HistoryIncome.objects.select_for_update().get(pk=pk)
        except HistoryIncome.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if timezone.now() - income.created > timedelta(days=14):
            return Response({"error": "Cannot edit incomes older than 14 days"},
                            status=status.HTTP_403_FORBIDDEN)

        old_amount = income.amount
        old_account_id = income.account["id"]

        serializer = HistoryIncomeEditSerializer(data=request.data, partial=True)

        if serializer.is_valid():
            if 'amount' in serializer.validated_data:
                new_amount = serializer.validated_data['amount']
                income.amount = new_amount
            else:
                new_amount = old_amount

            if 'account' in serializer.validated_data:
                new_account_id = serializer.validated_data['account']
            else:
                new_account_id = old_account_id

            if 'comment' in serializer.validated_data:
                income.comment = serializer.validated_data['comment']

            if old_account_id != new_account_id or old_amount != new_amount:
                try:
                    old_account = Account.objects.get(pk=old_account_id)
                    old_account.balance -= old_amount
                    old_account.save()
                except ObjectDoesNotExist:
                    pass

                try:
                    new_account = Account.objects.get(pk=new_account_id)
                    new_account.balance += new_amount
                    new_account.save()
                    income.account = {
                        'id': new_account.id,
                        'title': new_account.title,
                        'balance': float(new_account.balance),
                        'currency': new_account.currency,
                        'included_in_total_balance': new_account.included_in_total_balance,
                        'father_space': new_account.father_space.id
                    }
                except ObjectDoesNotExist:
                    return Response({"error": f"Account with id {new_account_id} does not exist"},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                new_account = Account.objects.get(pk=old_account_id)

            space = Space.objects.select_for_update().get(pk=income.father_space_id)
            total_balance = TotalBalance.objects.get(father_space=space)
            total_balance.balance -= convert_currencies(amount=old_amount,
                                                        from_currency=income.currency,
                                                        to_currency=space.currency)
            total_balance.balance += convert_currencies(amount=new_amount,
                                                        from_currency=new_account.currency,
                                                        to_currency=space.currency)
            total_balance.save()

            income.amount_in_default_currency = convert_currencies(
                amount=float(new_amount),
                from_currency=new_account.currency,
                to_currency=space.currency
            )

            income.new_balance = total_balance.balance
            income.currency = new_account.currency
            income.save()

            return Response({"message": "Income has been updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    patch = put

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        permission = CanDeleteHistory()
        if not permission.has_permission(request, self):
            return Response({"error": "You don't have permission to delete this history record"},
                            status=status.HTTP_403_FORBIDDEN)
        try:
            income = HistoryIncome.objects.select_for_update().get(pk=pk)
        except HistoryIncome.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if timezone.now() - income.created > timedelta(days=14):
            return Response({"error": "Cannot delete incomes older than 14 days"},
                            status=status.HTTP_403_FORBIDDEN)

        old_amount = income.amount
        old_account_id = income.account["id"]

        try:
            account = Account.objects.get(pk=old_account_id)
            account.balance -= old_amount
            account.save()
        except ObjectDoesNotExist:
            pass

        space = Space.objects.select_for_update().get(pk=income.father_space_id)
        total_balance = TotalBalance.objects.get(father_space=space)
        total_balance.balance -= convert_currencies(amount=old_amount,
                                                    from_currency=income.currency,
                                                    to_currency=space.currency)
        total_balance.save()

        income.delete()

        return Response({"message": "Income has been deleted successfully"}, status=status.HTTP_200_OK)


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
                icon_name = expense.to_cat.get('icon')
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
        tz = pytz.timezone(zone="UTC")
        now = datetime.now(tz)
        week_ago = now - timezone.timedelta(days=6)
        month_ago = now - timezone.timedelta(days=29)
        three_month_ago = now - timezone.timedelta(days=89)
        year_ago = now - timezone.timedelta(days=364)
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
    def get_summary(expenses: List[HistoryExpense]) -> dict[str, int]:
        category_expenses = sum(expense.amount for expense in expenses if expense.to_cat)
        loss_expenses = sum(expense.amount for expense in expenses if expense.to_cat is None)
        recurring_expenses = sum(expense.amount for expense in expenses if expense.periodic_expense)
        return {
            'Category': category_expenses,
            'Loss': loss_expenses,
            'Recurring Spending': recurring_expenses,
        }

    @staticmethod
    def get_total_expenses(summary: dict[str, int]) -> int:
        return sum(summary.values())

    def get_daily_percentages(self, daily_expenses: dict[str, List[HistoryExpense]], total_expenses: int) -> dict[str, dict[str, str]]:
        daily_percentages = {}
        for date_str, expenses in daily_expenses.items():
            day_summary = self.get_summary(expenses)
            percentages = self.get_percentages(day_summary, total_expenses)
            daily_percentages[date_str] = percentages
        return daily_percentages

    def get_percentages(self, summary: dict[str, int], total_expenses: int) -> dict[str, str]:
        if total_expenses == 0:
            return {key: '0 %' for key in summary}
        return {key: f"{round((val / total_expenses) * 100)} %" for key, val in summary.items()}

    def analyze_expenses(self, expenses: List[HistoryExpense], period: str) -> str:
        if not expenses:
            return f"You haven't made a single spending spree this {period}"
        summary = self.get_summary(expenses)
        total_expenses = self.get_total_expenses(summary)
        percentages = self.get_percentages(summary, total_expenses)
        max_category = max(percentages, key=lambda x: int(percentages[x].rstrip('%')))
        return f"The most you've spent this {period} on {max_category}"

    def format_result(self, expenses: List[HistoryExpense], request: Request) -> Dict:
        periods = self.get_periods(expenses)
        currency = Space.objects.get(pk=self.kwargs.get("space_pk")).currency
        result = {}

        for period, period_expenses in periods.items():
            result[period] = {}
            result[f"{period}_Percent"] = {}

            if not period_expenses:
                result[period] = f"0 {currency}"
                result[f"{period}_Percent"] = "0 %"
            else:
                period_summary = self.get_summary(period_expenses)
                total_expenses = self.get_total_expenses(period_summary)
                daily_expenses = {}
                for expense in period_expenses:
                    date_str = expense.created.date().strftime("%Y-%m-%d")
                    if date_str not in daily_expenses:
                        daily_expenses[date_str] = []
                    daily_expenses[date_str].append(expense)

                for date_str, day_expenses in daily_expenses.items():
                    day_summary = self.get_summary(day_expenses)
                    summary_with_currency = {key: f"{val} {currency}" for key, val in day_summary.items()}
                    result[period][date_str] = summary_with_currency

                daily_percentages = self.get_daily_percentages(daily_expenses, total_expenses)
                result[f"{period}_Percent"] = daily_percentages

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
        goal = transfer.to_goal.get("title")
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
            goal = transfer.to_goal.get("title")
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
        data = {
            "Week": self.get_data_and_percentages(6, space_pk),
            "Month": self.get_data_and_percentages(29, space_pk),
            "Three_month": self.get_data_and_percentages(89, space_pk),
            "Year": self.get_data_and_percentages(364, space_pk)
        }

        # Удаление пустых записей
        data = {period: values for period, values in data.items() if values}

        # Добавление текстового анализа
        for period in data:
            data[period]["analysis"] = self.get_analysis_message(data[period], period)

        return Response(data)

    def get_data_and_percentages(self, days, space_pk):
        period_data, initial_balance = self.get_data_for_period(days, space_pk)

        # Если период пуст, пытаемся получить последние данные до начала периода
        if not period_data:
            last_data_before_period = self.get_last_record_before_date(
                datetime.now() - timedelta(days=days), space_pk
            )
            if last_data_before_period is not None:
                period_data = {
                    (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'): last_data_before_period
                }
                initial_balance = last_data_before_period

        if not period_data:
            return {}

        percentages = self.calculate_percentages(period_data, initial_balance)
        return {
            "balance": period_data,
            "percentages": percentages,
        }

    def get_data_for_period(self, days, space_pk):
        tz = pytz.timezone('UTC')
        start_date = make_aware(datetime.now() - timedelta(days=days), tz) if is_naive(
            datetime.now()) else datetime.now() - timedelta(days=days)
        end_date = make_aware(datetime.now(), tz) if is_naive(datetime.now()) else datetime.now()

        expenses = list(HistoryExpense.objects.filter(
            created__range=[start_date, end_date],
            father_space_id=space_pk
        ).values('created', 'new_balance').order_by('created'))

        incomes = list(HistoryIncome.objects.filter(
            created__range=[start_date, end_date],
            father_space_id=space_pk
        ).values('created', 'new_balance').order_by('created'))

        combined_records = sorted(expenses + incomes, key=lambda x: x['created'])

        if not combined_records:
            return {}, Decimal('0')

        period_data = {}
        for record in combined_records:
            date_str = record['created'].strftime('%Y-%m-%d')
            period_data[date_str] = record['new_balance']

        initial_balance = self.get_initial_balance(start_date, space_pk)

        # Гарантируем, что данные за первый день периода присутствуют
        start_date_str = start_date.strftime('%Y-%m-%d')
        if start_date_str not in period_data:
            last_record_before_start = self.get_last_record_before_date(start_date, space_pk)
            period_data[start_date_str] = last_record_before_start

        # Сортируем данные по дате
        period_data = dict(sorted(period_data.items()))

        return period_data, initial_balance

    @staticmethod
    def get_initial_balance(start_date, space_pk):
        earliest_expense = HistoryExpense.objects.filter(
            created__lt=start_date,
            father_space_id=space_pk
        ).order_by('-created').first()

        earliest_income = HistoryIncome.objects.filter(
            created__lt=start_date,
            father_space_id=space_pk
        ).order_by('-created').first()

        earliest_record = None
        if earliest_expense and earliest_income:
            earliest_record = earliest_expense if earliest_expense.created > earliest_income.created else earliest_income
        elif earliest_expense:
            earliest_record = earliest_expense
        elif earliest_income:
            earliest_record = earliest_income

        return earliest_record.new_balance if earliest_record else Decimal('0')

    def get_last_record_before_date(self, date, space_pk):
        last_expense_before_start = HistoryExpense.objects.filter(
            created__lt=date,
            father_space_id=space_pk
        ).order_by('-created').first()

        last_income_before_start = HistoryIncome.objects.filter(
            created__lt=date,
            father_space_id=space_pk
        ).order_by('-created').first()

        last_record_before_start = None
        if last_expense_before_start and last_income_before_start:
            last_record_before_start = last_expense_before_start if last_expense_before_start.created > last_income_before_start.created else last_income_before_start
        elif last_expense_before_start:
            last_record_before_start = last_expense_before_start
        elif last_income_before_start:
            last_record_before_start = last_income_before_start

        return last_record_before_start.new_balance if last_record_before_start else Decimal('0')

    def calculate_percentages(self, period_data, initial_balance):
        percentages = {}
        for date, balance in period_data.items():
            percentage = (balance / initial_balance) * 100 if initial_balance != Decimal('0') else 0
            percentages[date] = f"{round(percentage, 2)}%"
        return percentages

    def get_analysis_message(self, period_data, period):
        balances = period_data.get('balance', {})
        if not balances:
            return f"No data available for the {period.lower()}."

        start_date = min(balances.keys())
        end_date = max(balances.keys())
        start_balance = balances[start_date]
        end_balance = balances[end_date]
        difference = end_balance - start_balance

        if difference > 0:
            return f"You have {difference} USD more this {period.lower()}."
        elif difference < 0:
            return f"You have {abs(difference)} USD less this {period.lower()}."
        else:
            return f"Your balance remained the same this {period.lower()}."


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
        summary = {}
        for expense in expenses:
            if expense.to_cat:
                category_title = expense.to_cat.get('title')
                amount = expense.amount_in_default_currency
                summary[category_title] = summary.get(category_title, 0) + amount
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
            max_spending_category, max_spending_amount = max(summary.items(), key=lambda x: x[1])
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
        account_json = {
            'id': account.id,
            'title': account.title,
            'balance': float(account.balance),
            'currency': account.currency
        }

        income_data = [
            {'amount': 1500, 'amount_in_default_currency': 1500, 'currency': 'USD',
             'account': account_json, 'created': datetime(2024, 6, 1), 'comment': '', 'new_balance': 1034},
            {'amount': 100, 'amount_in_default_currency': 100, 'currency': 'USD',
             'account': account_json, 'created': datetime(2024, 6, 4), 'comment': '', 'new_balance': 10245},
            {'amount': 1500, 'amount_in_default_currency': 1500, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2024, 6, 1), 'comment': '', 'new_balance': 1034},
            {'amount': 100, 'amount_in_default_currency': 100, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2024, 6, 4), 'comment': '', 'new_balance': 10245},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2024, 6, 5), 'comment': '', 'new_balance': 14},
            {'amount': 1500, 'amount_in_default_currency': 1500, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2024, 6, 15), 'comment': '', 'new_balance': 1034},
            {'amount': 50, 'amount_in_default_currency': 50, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2024, 6, 13), 'comment': '', 'new_balance': 901},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2024, 6, 11), 'comment': '', 'new_balance': 700},
            {'amount': 1900, 'amount_in_default_currency': 1900, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2024, 6, 9), 'comment': '', 'new_balance': 1039},
            {'amount': 500, 'amount_in_default_currency': 500, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2023, 12, 30), 'comment': '', 'new_balance': 2000},
            {'amount': 390, 'amount_in_default_currency': 390, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2024, 3, 5), 'comment': '', 'new_balance': 3256},
            {'amount': 1500, 'amount_in_default_currency': 1500, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2023, 1, 1), 'comment': '', 'new_balance': 901},
            {'amount': 100, 'amount_in_default_currency': 100, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2023, 3, 1), 'comment': '', 'new_balance': 941},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2023, 5, 1), 'comment': '', 'new_balance': 23456},
            {'amount': 1500, 'amount_in_default_currency': 1500, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2023, 9, 1), 'comment': '', 'new_balance': 9344},
            {'amount': 50, 'amount_in_default_currency': 50, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2023, 11, 1), 'comment': '', 'new_balance': 901},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2023, 12, 1), 'comment': '', 'new_balance': 601},
            {'amount': 1900, 'amount_in_default_currency': 1900, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2023, 12, 15), 'comment': '', 'new_balance': 941},
            {'amount': 500, 'amount_in_default_currency': 500, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2023, 12, 30), 'comment': '', 'new_balance': 546},
            {'amount': 390, 'amount_in_default_currency': 390, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2024, 3, 5), 'comment': '', 'new_balance': 9023},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2024, 4, 10), 'comment': '', 'new_balance': 901},
            {'amount': 2000, 'amount_in_default_currency': 2000, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2024, 4, 19), 'comment': '', 'new_balance': 101},
            {'amount': 300, 'amount_in_default_currency': 300, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2024, 4, 20), 'comment': '', 'new_balance': 9781},
            {'amount': 900, 'amount_in_default_currency': 900, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2024, 4, 22), 'comment': '', 'new_balance': 9011},
            {'amount': 10000, 'amount_in_default_currency': 10000, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2024, 4, 24), 'comment': '', 'new_balance': 2301},
            {'amount': 1000, 'amount_in_default_currency': 100, 'father_space': father_space, 'currency': 'USD',
             'account': account_json, 'created': datetime(2024, 4, 25), 'comment': '', 'new_balance': 911}
        ]

        incomes = [HistoryIncome(
            father_space=father_space,
            amount=data['amount'],
            amount_in_default_currency=data['amount_in_default_currency'],
            currency=data['currency'],
            account=data['account'],
            created=data['created'],
            comment=data['comment'],
            new_balance=data['new_balance']
        ) for data in income_data]

        HistoryIncome.objects.bulk_create(incomes)
        return HistoryIncome.objects.filter(father_space=father_space)


class ExpenseAutoDataView(generics.ListAPIView):
    permission_classes = ()
    serializer_class = HistoryExpenseAutoDataSerializer

    def get_queryset(self):
        father_space_id = self.kwargs["space_pk"]
        father_space = Space.objects.get(id=father_space_id)
        account = Account.objects.create(title='Cash', balance=1000, currency='USD', father_space=father_space)
        account_json = {
            'id': account.id,
            'title': account.title,
            'balance': float(account.balance),
            'currency': account.currency
        }

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
        categories = {
            name: Category.objects.create(
                title=name,
                spent=100,
                limit=10000,
                color='#a3e12f',
                icon='FORWARD',
                father_space=father_space
            )
            for name in category_names
        }
        categories_json = {
            name: {
                'id': category.id,
                'title': category.title,
                'spent': float(category.spent),
                'limit': float(category.limit),
                'color': category.color,
                'icon': category.icon
            }
            for name, category in categories.items()
        }

        expense_data = [
            {
                'amount': 750,
                'amount_in_default_currency': 750,
                'father_space': father_space,
                'currency': 'USD',
                'periodic_expense': True,
                'from_acc': account_json,
                'created': datetime(2024, 6, 15),
                'comment': '',
                'to_cat': categories_json['Food'],
                'new_balance': 10000
            },
            {
                'amount': 1000,
                'amount_in_default_currency': 1000,
                'father_space': father_space,
                'currency': 'USD',
                'from_acc': account_json,
                'created': datetime(2024, 6, 14),
                'comment': '',
                'to_cat': categories_json['Home'],
                'new_balance': 901
            },
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2024, 6, 15),
             'comment': '', 'to_cat': categories_json['Food'], 'new_balance': 10000},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 6, 14), 'comment': '', 'to_cat': categories_json['Home'],
             'new_balance': 901},
            {'amount': 2000, 'amount_in_default_currency': 2000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 6, 9), 'comment': '', 'to_cat': categories_json['Food'],
             'new_balance': 9011},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2024, 5, 11),
             'comment': '', 'to_cat': categories_json['Food'], 'new_balance': 1111},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 6, 10), 'comment': '', 'to_cat': categories_json['Home'],
             'new_balance': 981},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 6, 2), 'comment': '', 'to_cat': categories_json['Food'],
             'new_balance': 829},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 6, 13), 'comment': '', 'to_cat': categories_json['Food'],
             'new_balance': 283},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 5, 30), 'comment': '', 'to_cat': categories_json['Home'],
             'new_balance': 9056},
            {'amount': 100, 'amount_in_default_currency': 100, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 6, 6), 'comment': '', 'to_cat': categories_json['Food'],
             'new_balance': 9012},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 6, 2), 'comment': '', 'to_cat': categories_json['Home'],
             'new_balance': 901},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2023, 1, 30),
             'comment': '', 'to_cat': categories_json['Food'], 'new_balance': 9349},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2023, 3, 20), 'comment': '', 'to_cat': categories_json['Home'],
             'new_balance': 2300},
            {'amount': 2000, 'amount_in_default_currency': 2000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2023, 5, 11), 'comment': '', 'to_cat': categories_json['Food'],
             'new_balance': 1234},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2023, 9, 11),
             'comment': '', 'to_cat': categories_json['Food'], 'new_balance': 10325},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 3, 10), 'comment': '', 'to_cat': categories_json['Home'],
             'new_balance': 23456},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 2, 2), 'comment': '', 'to_cat': categories_json['Food'],
             'new_balance': 43289},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 2, 16), 'comment': '', 'to_cat': categories_json['Food'],
             'new_balance': 1454},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 1, 31), 'comment': '', 'to_cat': categories_json['Home'],
             'new_balance': 10},
            {'amount': 100, 'amount_in_default_currency': 100, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 3, 6), 'comment': '', 'to_cat': categories_json['Food'],
             'new_balance': 100},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 4, 2), 'comment': '', 'to_cat': categories_json['Home'],
             'new_balance': 100000},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2024, 5, 3),
             'comment': '', 'to_cat': categories_json['Food'], 'new_balance': 10000},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2024, 5, 3),
             'comment': '', 'to_cat': categories_json['Utilities'], 'new_balance': 1000},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2024, 5, 3),
             'comment': '', 'to_cat': categories_json['Subscription'], 'new_balance': 100},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2024, 5, 3),
             'comment': '', 'to_cat': categories_json['Insurance'], 'new_balance': 10},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2024, 5, 3),
             'comment': '', 'to_cat': categories_json['Transportation'], 'new_balance': 10000},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 5, 4), 'comment': '', 'to_cat': categories_json['Food'],
             'new_balance': 4615},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 5, 5), 'comment': '', 'to_cat': categories_json['Home'],
             'new_balance': 859},
            {'amount': 750, 'amount_in_default_currency': 750, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 5, 6), 'comment': '', 'to_cat': categories_json['Food'],
             'new_balance': 498},
            {'amount': 2000, 'amount_in_default_currency': 2000, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2024, 5, 8), 'comment': '',
             'to_cat': categories_json['Home'], 'new_balance': 8622},
            {'amount': 50, 'amount_in_default_currency': 50, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 5, 15), 'comment': '',
             'to_cat': categories_json['Entertainment'], 'new_balance': 555},
            {'amount': 75, 'amount_in_default_currency': 75, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 5, 16), 'comment': '',
             'to_cat': categories_json['Transportation'], 'new_balance': 10085},
            {'amount': 120, 'amount_in_default_currency': 120, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 5, 17), 'comment': '', 'to_cat': categories_json['Health'],
             'new_balance': 6565},
            {'amount': 200, 'amount_in_default_currency': 200, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 5, 18), 'comment': '', 'to_cat': categories_json['Gifts'],
             'new_balance': 19896},
            {'amount': 80, 'amount_in_default_currency': 80, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 5, 19), 'comment': '', 'to_cat': categories_json['Education'],
             'new_balance': 854},
            {'amount': 300, 'amount_in_default_currency': 300, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 5, 20), 'comment': '',
             'to_cat': categories_json['Entertainment'], 'new_balance': 858},
            {'amount': 120, 'amount_in_default_currency': 120, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 5, 21), 'comment': '', 'to_cat': categories_json['Gifts'],
             'new_balance': 11},
            {'amount': 60, 'amount_in_default_currency': 60, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_json, 'created': datetime(2024, 5, 22), 'comment': '',
             'to_cat': categories_json['Transportation'], 'new_balance': 188},
            {'amount': 25, 'amount_in_default_currency': 25, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2024, 5, 13),
             'comment': 'Еженедельная подписка', 'to_cat': categories_json['Subscription'], 'new_balance': 555},
            {'amount': 100, 'amount_in_default_currency': 100, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2023, 10, 1),
             'comment': 'Годовая страховка авто', 'to_cat': categories_json['Insurance'], 'new_balance': 135},
            {'amount': 80, 'amount_in_default_currency': 80, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2024, 3, 15),
             'comment': 'Квартальная арендная плата', 'to_cat': categories_json['Rent'], 'new_balance': 4685},
            {'amount': 300, 'amount_in_default_currency': 300, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2024, 5, 1),
             'comment': 'Полугодовая плата за обучение', 'to_cat': categories_json['Education'], 'new_balance': 88},
            {'amount': 40, 'amount_in_default_currency': 40, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2024, 5, 11),
             'comment': 'Еженедельные расходы на транспорт', 'to_cat': categories_json['Transportation'],
             'new_balance': 444},
            {'amount': 1500, 'amount_in_default_currency': 1500, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2024, 3, 15),
             'comment': 'Годовая плата за обслуживание', 'to_cat': categories_json['Maintenance'], 'new_balance': 55},
            {'amount': 60, 'amount_in_default_currency': 60, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2024, 5, 15),
             'comment': 'Ежемесячная плата за фитнес', 'to_cat': categories_json['Sports'], 'new_balance': 65456},
            {'amount': 200, 'amount_in_default_currency': 200, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2024, 4, 1),
             'comment': 'Квартальная оплата интернета', 'to_cat': categories_json['Utilities'], 'new_balance': 1465},
            {'amount': 125, 'amount_in_default_currency': 125, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2024, 5, 24),
             'comment': 'Ежегодный платеж за парковку', 'to_cat': categories_json['Parking'], 'new_balance': 546},
            {'amount': 3464, 'amount_in_default_currency': 3464, 'father_space': father_space, 'currency': 'USD',
             'periodic_expense': True, 'from_acc': account_json, 'created': datetime(2024, 5, 24),
             'comment': 'Ежегодный платеж за парковку', 'to_cat': categories_json['Park'], 'new_balance': 55}
        ]

        expenses = [
            HistoryExpense(
                father_space=data['father_space'],
                amount=data['amount'],
                amount_in_default_currency=data['amount_in_default_currency'],
                currency=data['currency'],
                periodic_expense=data.get('periodic_expense', False),
                from_acc=data['from_acc'],
                to_cat=data['to_cat'],
                created=data['created'],
                comment=data['comment'],
                new_balance=data['new_balance']
            )
            for data in expense_data
        ]

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

        account_data = {
            'id': account.id,
            'title': account.title,
            'balance': account.balance,
            'currency': account.currency
        }

        goal_main1_data = {
            'id': goal_main1.id,
            'title': goal_main1.title,
            'goal': goal_main1.goal,
            'collected': goal_main1.collected
        }

        goal_main2_data = {
            'id': goal_main2.id,
            'title': goal_main2.title,
            'goal': goal_main2.goal,
            'collected': goal_main2.collected
        }

        transfer_data = [
            {'amount': 100, 'amount_in_default_currency': 100, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 5, 22),
             'to_goal': goal_main1_data,
             'from_goal': goal_main2_data, 'goal_amount': 4000},
            {'amount': 100, 'amount_in_default_currency': 100, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 5, 22), 'to_goal': goal_main1_data,
             'from_goal': goal_main2_data, 'goal_amount': 4000},
            {'amount': 150, 'amount_in_default_currency': 150, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 6, 15), 'to_goal': goal_main1_data,
             'from_goal': goal_main2_data, 'goal_amount': 4000},
            {'amount': 200, 'amount_in_default_currency': 200, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 6, 14), 'to_goal': goal_main2_data,
             'from_goal': goal_main1_data, 'goal_amount': 3000},
            {'amount': 250, 'amount_in_default_currency': 250, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 6, 13), 'to_goal': goal_main2_data,
             'from_goal': goal_main1_data, 'goal_amount': 3000},
            {'amount': 300, 'amount_in_default_currency': 300, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 6, 12), 'to_goal': goal_main2_data,
             'from_goal': goal_main1_data, 'goal_amount': 3000},
            {'amount': 400, 'amount_in_default_currency': 400, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 6, 1), 'to_goal': goal_main1_data,
             'from_goal': goal_main2_data, 'goal_amount': 4000},
            {'amount': 500, 'amount_in_default_currency': 500, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 5, 17), 'to_goal': goal_main1_data,
             'from_goal': goal_main2_data, 'goal_amount': 4000},
            {'amount': 600, 'amount_in_default_currency': 600, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 5, 15), 'to_goal': goal_main2_data,
             'from_goal': goal_main1_data, 'goal_amount': 3000},
            {'amount': 700, 'amount_in_default_currency': 700, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 5, 22), 'to_goal': goal_main2_data,
             'from_goal': goal_main1_data, 'goal_amount': 3000},
            {'amount': 800, 'amount_in_default_currency': 800, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 5, 29), 'to_goal': goal_main2_data,
             'from_goal': goal_main1_data, 'goal_amount': 3000},
            {'amount': 100, 'amount_in_default_currency': 100, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 5, 22), 'to_goal': goal_main1_data,
             'from_goal': goal_main2_data, 'goal_amount': 4000},
            {'amount': 150, 'amount_in_default_currency': 150, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 5, 23), 'to_goal': goal_main1_data,
             'from_goal': goal_main2_data, 'goal_amount': 4000},
            {'amount': 200, 'amount_in_default_currency': 200, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 5, 24), 'to_goal': goal_main2_data,
             'from_goal': goal_main1_data, 'goal_amount': 3000},
            {'amount': 250, 'amount_in_default_currency': 250, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 5, 25), 'to_goal': goal_main2_data,
             'from_goal': goal_main1_data, 'goal_amount': 3000},
            {'amount': 300, 'amount_in_default_currency': 300, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 5, 26), 'to_goal': goal_main2_data,
             'from_goal': goal_main1_data, 'goal_amount': 3000},
            {'amount': 400, 'amount_in_default_currency': 400, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 5, 1), 'to_goal': goal_main1_data,
             'from_goal': goal_main2_data, 'goal_amount': 4000},
            {'amount': 500, 'amount_in_default_currency': 500, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 5, 8), 'to_goal': goal_main1_data,
             'from_goal': goal_main2_data, 'goal_amount': 4000},
            {'amount': 600, 'amount_in_default_currency': 600, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 5, 15), 'to_goal': goal_main2_data,
             'from_goal': goal_main1_data, 'goal_amount': 3000},
            {'amount': 700, 'amount_in_default_currency': 700, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 5, 22), 'to_goal': goal_main2_data,
             'from_goal': goal_main1_data, 'goal_amount': 3000},
            {'amount': 800, 'amount_in_default_currency': 800, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 5, 29), 'to_goal': goal_main2_data,
             'from_goal': goal_main1_data, 'goal_amount': 3000},
            {'amount': 900, 'amount_in_default_currency': 900, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 4, 1), 'to_goal': goal_main1_data,
             'from_goal': goal_main2_data, 'goal_amount': 4000},
            {'amount': 1000, 'amount_in_default_currency': 1000, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 4, 15), 'to_goal': goal_main1_data,
             'from_goal': goal_main2_data, 'goal_amount': 4000},
            {'amount': 1100, 'amount_in_default_currency': 1100, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 4, 22), 'to_goal': goal_main2_data,
             'from_goal': goal_main1_data, 'goal_amount': 3000},
            {'amount': 1200, 'amount_in_default_currency': 1200, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 5, 1), 'to_goal': goal_main2_data,
             'from_goal': goal_main1_data, 'goal_amount': 3000},
            {'amount': 1300, 'amount_in_default_currency': 1300, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2024, 5, 15), 'to_goal': goal_main2_data,
             'from_goal': goal_main1_data, 'goal_amount': 3000},
            {'amount': 1400, 'amount_in_default_currency': 1400, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2023, 6, 1), 'to_goal': goal_main1_data,
             'from_goal': goal_main2_data, 'goal_amount': 4000},
            {'amount': 1500, 'amount_in_default_currency': 1500, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2023, 7, 1), 'to_goal': goal_main1_data,
             'from_goal': goal_main2_data, 'goal_amount': 4000},
            {'amount': 1600, 'amount_in_default_currency': 1600, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2023, 8, 1), 'to_goal': goal_main2_data,
             'from_goal': goal_main1_data, 'goal_amount': 3000},
            {'amount': 1700, 'amount_in_default_currency': 1700, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2023, 9, 1), 'to_goal': goal_main2_data,
             'from_goal': goal_main1_data, 'goal_amount': 3000},
            {'amount': 1800, 'amount_in_default_currency': 1800, 'father_space': father_space, 'currency': 'USD',
             'from_acc': account_data, 'to_acc': account_data, 'created': datetime(2023, 10, 1), 'to_goal': goal_main2_data,
             'from_goal': goal_main1_data, 'goal_amount': 3000}
        ]
        transfers = [HistoryTransfer(**data) for data in transfer_data]
        HistoryTransfer.objects.bulk_create(transfers)

        return HistoryTransfer.objects.filter(father_space=father_space)
