from datetime import datetime
from decimal import Decimal

from drf_multiple_model.views import ObjectMultipleModelAPIView
from rest_framework import generics
from django.db.models import Sum
from django.http import JsonResponse

from backend.apps.history.models import HistoryIncome, HistoryExpense
from backend.apps.history.serializers import HistoryExpenseSerializer, DailyIncomeSerializer, HistoryAutoDataSerializer
from backend.apps.account.models import Account
from backend.apps.category.models import Category


from rest_framework import generics
from rest_framework.views import APIView
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


class AutoDataView(generics.ListAPIView):
    permission_classes = ()
    serializer_class = HistoryAutoDataSerializer

    def get_queryset(self):
        father_space = self.kwargs["space_pk"]
        income_data = [
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 1, 1), 'comment': ''},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 3, 1), 'comment': ''},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 5, 1), 'comment': ''},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 9, 1), 'comment': ''},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 11, 1), 'comment': ''},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 12, 1), 'comment': ''},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 12, 15), 'comment': ''},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2023, 12, 30), 'comment': ''},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 5), 'comment': ''},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 10), 'comment': ''},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 20), 'comment': ''},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 24), 'comment': ''},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 25), 'comment': ''},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 29), 'comment': ''},
            {'amount': 1000, 'father_space': father_space, 'currency': 'USD',
             'account': 'Cash', 'created': datetime(2024, 3, 31), 'comment': ''}
        ]

        for data in income_data:
            serializer = HistoryAutoDataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HistoryExpenseEdit(APIView):
    permission_classes = ()    
    def put(self, request, pk, *args, **kwargs):
        try:
            expense = HistoryExpense.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = HistoryExpenseSerializer(expense, data=request.data)

        if serializer.is_valid():
            amount = request.data.get("amount")
            account = Account.objects.filter(title=expense.from_acc).first()
            category = Category.objects.filter(title=expense.to_cat).first()

            account.balance += Decimal(amount)

            if category:
                category.spent -= Decimal(amount)

            serializer.save()
            return Response({"massage":"Expense has been updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        try:
            expense = HistoryExpense.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = HistoryExpenseSerializer(expense, data=request.data)

        if serializer.is_valid():
            amount = request.data.get("amount")
            account = Account.objects.filter(title=expense.from_acc).first()
            category = Category.objects.filter(title=expense.to_cat).first()

            account.balance += Decimal(amount)

            if category:
                category.spent -= Decimal(amount)

            serializer.save()
            return Response({"massage":"Expense has been updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, *args, **kwargs):

        expense = HistoryExpense.objects.get(pk=pk)

        amount = expense.amount
        account = Account.objects.filter(title=expense.from_acc).first()
        category = Category.objects.filter(title=expense.to_cat).first()

        account.balance += Decimal(amount)
        category.spent -= Decimal(amount)

        expense.delete()

        return Response({"massage":"Expense has been updated successfully"}, status=status.HTTP_204_NO_CONTENT)


class HistoryIncomeEdit(APIView):
    permission_classes = ()    
    def put(self, request, pk, *args, **kwargs):
        try:
            income = HistoryIncome.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = HistoryIncomeSerializer(income, data=request.data)

        amount_befor_changing = income.amount

        if serializer.is_valid():
            amount = request.data.get("amount")
            account = Account.objects.filter(title=income.account).first()


            account.balance += Decimal(amount) - Decimal(amount_befor_changing)
            serializer.save()
            return Response({"massage":"Expense has been updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        try:
            income = HistoryIncome.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = HistoryIncomeSerializer(income, data=request.data)

        amount_befor_changing = income.amount

        if serializer.is_valid():
            amount = request.data.get("amount")
            account = Account.objects.filter(title=income.account).first()


            account.balance += Decimal(amount) - Decimal(amount_befor_changing)
            serializer.save()
            return Response({"massage":"Expense has been updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, *args, **kwargs):

        income = HistoryIncome.objects.get(pk=pk)

        amount = income.amount
        account = Account.objects.filter(title=income.account).first()

        account.balance -= amount

        income.delete()

        return Response({"massage":"Expense has been updated successfully"}, status=status.HTTP_204_NO_CONTENT)
