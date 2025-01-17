from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from backend.apps.adminpanel.models import ProjectOverview
from backend.apps.tink.models import TinkAccount
from backend.apps.history.models import HistoryExpense, HistoryIncome, HistoryTransfer
from backend.apps.tink.models import TinkUser
from backend.apps.category.models import Category 
from backend.apps.goal.models import Goal 
from backend.apps.spend.models import PeriodicSpendCounter 
from backend.apps.adminpanel.serializers import ProjectOverviewSerializer
from backend.apps.store.models import PaymentHistory
from backend.apps.store.serializers import PaymentHistorySerializer
from rest_framework import generics
from collections import defaultdict
from django.utils import timezone


class ProjectOverviewView(APIView):
    def get(self, request, space_pk):
        tink_user = TinkUser.objects.filter(space_id=space_pk).first()
        existing_records = ProjectOverview.objects.filter(space_id=space_pk)
        current_month = timezone.now().month
        current_year = timezone.now().year

        last_payment = PaymentHistory.objects.filter(
            father_space=space_pk,
            payment_category='service'
        ).order_by('-date').first()

        # Вычисляем количество месяцев с последней оплаты
        months_since_payment = 1
        if last_payment:
            current_date = timezone.now().date()
            last_payment_date = last_payment.date
            months_since_payment = (
                (current_date.year - last_payment_date.year) * 12 +
                current_date.month - last_payment_date.month
            )
        
        # Проверяем наличие оплаты за текущий месяц
        has_payment = PaymentHistory.objects.filter(
            father_space=space_pk,
            payment_category='service',
            date__year=current_year,
            date__month=current_month
        ).exists()

        cards_count = TinkAccount.objects.filter(user_id=tink_user).count()
        accounts_count = TinkAccount.objects.filter(user_id=tink_user).count()
        categories_count = Category.objects.filter(father_space_id=space_pk).count() 
        goals_count = Goal.objects.filter(father_space_id=space_pk).count()
        periods_count = PeriodicSpendCounter.objects.filter(father_space_id=space_pk).count()
        incomes = HistoryExpense.objects.filter(
            father_space_id=space_pk,
            tink_account_id__isnull=False,
            created__year=current_year,
            created__month=current_month
        ).count()

        expenses = HistoryIncome.objects.filter(
            father_space_id=space_pk,
            tink_account_id__isnull=False,
            created__year=current_year,
            created__month=current_month
        ).count()
        ai_count = (incomes + expenses) * 0.001

        structures_count = accounts_count + categories_count + goals_count + periods_count

        storage_data_count = (
            HistoryExpense.objects.filter(father_space_id=space_pk).count() +
            HistoryIncome.objects.filter(father_space_id=space_pk).count() +
            HistoryTransfer.objects.filter(father_space_id=space_pk).count()
        ) * 0.003

        # Если есть оплата, добавляем updated_date равным дате последней оплаты
        response_data = [
            {
                "assets": "Cards",
                "data": cards_count,
                "price": 0
            },
            {
                "assets": "Structures",
                "data": structures_count,
                "price": 0,
            },
            {
                "assets": "Storage data",
                "data": storage_data_count,
                "price": 0,
            },
            {
                "assets": "AI utilization",
                "data": ai_count,
                "price": 0,
            },
        ]

        # Если есть оплата, добавляем updated_date
        if has_payment and last_payment:
            updated_date = last_payment.date
            for item in response_data:
                item["updated_date"] = updated_date
            return Response(response_data)

        if not existing_records.exists():

            records = [
                {
                    "assets": "Cards",
                    "data": cards_count,
                    "price": cards_count * 0.7 * months_since_payment,
                },
                {
                    "assets": "Structures",
                    "data": structures_count,
                    "price": structures_count * 0.03 * months_since_payment,
                },
                {
                    "assets": "Storage data",
                    "data": storage_data_count,
                    "price": max(round(storage_data_count, 1), 0.1) * months_since_payment,
                },
                {
                    "assets": "AI utilization",
                    "data": ai_count,
                    "price": max(round(ai_count, 1), 0.1) * months_since_payment,
                },
            ]
            
            for record in records:
                ProjectOverview.objects.create(
                    space_id=space_pk,
                    assets=record["assets"],
                    data=record["data"],
                    price=record["price"],
                    updated_date=now().date()
                )
            existing_records = ProjectOverview.objects.filter(space_id=space_pk)

        else:
            for record in existing_records:
                if record.assets == "Cards":
                    new_data = TinkAccount.objects.filter(user_id=tink_user).count()
                    new_price = new_data * 0.7 * months_since_payment
                elif record.assets == "Structures":
                    new_data = (TinkAccount.objects.filter(user_id=space_pk).count() +
                                Category.objects.filter(father_space_id=space_pk).count() +
                                Goal.objects.filter(father_space_id=space_pk).count() +
                                PeriodicSpendCounter.objects.filter(father_space_id=space_pk).count())
                    new_price = new_data * 0.05 * months_since_payment
                elif record.assets == "Storage data":
                    new_data = (
                                HistoryExpense.objects.filter(father_space_id=space_pk, tink_account_id__isnull=False).count() +
                                HistoryIncome.objects.filter(father_space_id=space_pk, tink_account_id__isnull=False).count()
                    ) * 0.003
                    new_price = max(round(new_data, 1), 0.1) * months_since_payment

                elif record.assets == "AI utilization":
                    new_data = (
                        HistoryExpense.objects.filter(
                            father_space_id=space_pk,
                            tink_account_id__isnull=False,
                            created__year=current_year,
                            created__month=current_month
                        ).count() +
                        HistoryIncome.objects.filter(
                            father_space_id=space_pk,
                            tink_account_id__isnull=False,
                            created__year=current_year,
                            created__month=current_month
                        ).count() +
                        HistoryTransfer.objects.filter(father_space_id=space_pk).count()
                    ) * 0.001
                    new_price = max(round(new_data, 1), 0.1) * months_since_payment

                if record.data != new_data or record.price != new_price:
                    record.data = new_data
                    record.price = new_price
                    record.updated_date =now().date()
                    record.save()

        serializer = ProjectOverviewSerializer(existing_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TotalDeposits(generics.ListAPIView):
    serializer_class = PaymentHistorySerializer

    def get_queryset(self):
        space_id = self.kwargs.get('space_pk')

        return PaymentHistory.objects.filter(father_space=space_id).order_by('id')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        amounts = list(queryset.values_list('amount', flat=True))
        return Response(amounts)


class ServiceStatistic(generics.ListAPIView):
    serializer_class = PaymentHistorySerializer

    def get_queryset(self):
        space_id = self.kwargs['space_pk']
        current_year = timezone.now().year
        return PaymentHistory.objects.filter(
            father_space=space_id, 
            payment_category='service',
            date__year=current_year
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        monthly_stats = defaultdict(lambda: 0)
        for payment in queryset:
            month_year = payment.date.strftime('%b')
            monthly_stats[month_year] += payment.amount
        result = {month: str(amount) for month, amount in sorted(monthly_stats.items())}
        return Response(result)
