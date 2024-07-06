import anthropic
from django.conf import settings

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from django.db.models import Sum, F

from backend.apps.account.permissions import IsSpaceMember
from backend.apps.history.models import HistoryIncome, HistoryExpense, HistoryTransfer
from backend.apps.space.models import Space
from django.utils import timezone


class FinancialAdviceView(GenericAPIView):
    permission_classes = (IsSpaceMember,)

    def get_object(self):
        space = Space.objects.get(id=self.kwargs['space_pk'])
        return space

    def get(self, request, **kwargs):
        space_id = kwargs.get('space_pk')
        time_range = request.data.get('time_range', '30_days')

        try:
            space = self.get_object()
        except Space.DoesNotExist:
            return Response({"error": "Space not found"}, status=status.HTTP_404_NOT_FOUND)

        if time_range == 'month_to_date':
            start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # default to last 30 days
            start_date = timezone.now() - timedelta(days=30)

        income = HistoryIncome.objects.filter(
            father_space=space,
            created__gte=start_date
        ).aggregate(Sum('amount_in_default_currency'))['amount_in_default_currency__sum'] or 0

        expenses = HistoryExpense.objects.filter(
            father_space=space,
            created__gte=start_date
        ).aggregate(Sum('amount_in_default_currency'))['amount_in_default_currency__sum'] or 0

        categories = HistoryExpense.objects.filter(
            father_space=space,
            created__gte=start_date,
            to_cat__isnull=False
        ).aggregate(Sum('amount_in_default_currency'))['amount_in_default_currency__sum'] or 0

        recurring_payments = HistoryExpense.objects.filter(
            father_space=space,
            created__gte=start_date,
            periodic_expense=True
        ).aggregate(Sum('amount_in_default_currency'))['amount_in_default_currency__sum'] or 0

        goals = HistoryTransfer.objects.filter(
            father_space=space,
            created__gte=start_date,
            to_goal__isnull=False
        ).aggregate(Sum('amount_in_default_currency'))['amount_in_default_currency__sum'] or 0

        result = {
            "income": income,
            "expenses": expenses,
            "categories": categories,
            "recurring_payments": recurring_payments,
            "goals": goals,
            "time_range": time_range
        }

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        system_prompt = """
        You are Dowt, a friendly and knowledgeable financial advisor. Provide personalized financial advice based on the given financial data. Be encouraging and supportive in your advice. Use some beautiful phrases before concluding your response. End your advice with one of the following signatures:
        "Regards, Dowt."
        "Your financial advisor, Dowt."
        "Your Dowt."
        Remember to tailor your advice to the specific financial situation presented in the data.
        Note: User can't write you a message, so don't write something like 'If you need any clarification or have additional questions, feel free to ask. I am here to help you on your path to financial wellbeing.'
        """

        user_prompt = f"""
        Based on the following financial data for the {'last 30 days' if result['time_range'] == '30_days' else 'current month to date'}:
        Monthly Income: ${result['income']}
        Total Monthly Expenses: ${result['expenses']}
        Amount spent on categories (e.g., food, home, medicine, education): ${result['categories']}
        Amount spent on recurring payments (e.g., subscriptions): ${result['recurring_payments']}
        Amount saved for financial goals (e.g., new MacBook, better housing): ${result['goals']}
        Note: The total expenses include categories, recurring payments, and additional spending.
        Please provide advice on:
        1. Budgeting and expenditure management
        2. Cost reduction strategies
        3. Achieving financial goals
        4. Investment opportunities
        5. Additional Recommendations
        """

        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )

        advice = message.content[0].text
        return Response({"advice": advice})


class FinancialAdviceFromHistoryView(GenericAPIView):
    permission_classes = (IsSpaceMember,)

    def get_object(self):
        space = Space.objects.get(id=self.kwargs['space_pk'])
        return space

    def get(self, request, **kwargs):
        space_id = kwargs.get('space_pk')
        time_range = request.data.get('time_range', '30_days')

        try:
            space = self.get_object()
        except Space.DoesNotExist:
            return Response({"error": "Space not found"}, status=status.HTTP_404_NOT_FOUND)

        if time_range == 'month_to_date':
            start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # default to last 30 days
            start_date = timezone.now() - timedelta(days=30)

        # Получаем полную историю трат
        expenses = HistoryExpense.objects.filter(
            father_space=space,
            created__gte=start_date
        ).annotate(
            category_title=F('to_cat__title'),
            category_icon=F('to_cat__icon')
        ).values('amount', 'currency', 'comment', 'category_title', 'category_icon', 'periodic_expense', 'created')

        # Получаем доходы
        incomes = HistoryIncome.objects.filter(
            father_space=space,
            created__gte=start_date
        ).values('amount', 'currency', 'comment', 'created')

        # Получаем переводы
        transfers = HistoryTransfer.objects.filter(
            father_space=space,
            created__gte=start_date
        ).values('amount', 'currency', 'from_acc', 'to_acc', 'from_goal', 'to_goal', 'created')

        total_income = sum(income['amount'] for income in incomes)
        total_expenses = sum(expense['amount'] for expense in expenses)

        # Группируем траты по категориям
        category_expenses = {}
        for expense in expenses:
            category = expense['category_title'] or 'Uncategorized'
            if category not in category_expenses:
                category_expenses[category] = 0
            category_expenses[category] += expense['amount']

        result = {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "category_expenses": category_expenses,
            "expenses_history": list(expenses),
            "income_history": list(incomes),
            "transfer_history": list(transfers),
            "time_range": time_range
        }

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        system_prompt = """
        You are Dowt, a friendly and knowledgeable financial advisor. Analyze the given financial data and provide personalized advice on reducing expenses, optimizing finances, and achieving financial goals. Be specific in your recommendations, referring to actual spending patterns and categories. Use encouraging language and offer practical tips. End your advice with a signature like "Your financial advisor, Dowt."
        """

        user_prompt = f"""
        Based on the following financial data for the {'last 30 days' if result['time_range'] == '30_days' else 'current month to date'}:
        Total Income: ${result['total_income']}
        Total Expenses: ${result['total_expenses']}

        Expenses by category:
        {', '.join([f"{category}: ${amount}" for category, amount in result['category_expenses'].items()])}

        Detailed expense history:
        {result['expenses_history']}

        Income history:
        {result['income_history']}

        Transfer history:
        {result['transfer_history']}

        Please provide advice on:
        1. Specific areas where expenses can be reduced
        2. Strategies to optimize spending in the top expense categories
        3. Patterns in the spending history that could be improved
        4. Recommendations for better budgeting based on the income and expense ratio
        5. Suggestions for maximizing savings and achieving financial goals
        6. Any other financial insights or tips based on this data
        """

        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1500,
            temperature=0,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )

        advice = message.content[0].text
        return Response({"advice": advice})
