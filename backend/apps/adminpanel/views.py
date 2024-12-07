from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from backend.apps.adminpanel.models import ProjectOverview
from backend.apps.tink.models import TinkAccount
from backend.apps.history.models import HistoryExpense, HistoryIncome, HistoryTransfer
from backend.apps.category.models import Category 
from backend.apps.goal.models import Goal 
from backend.apps.spend.models import PeriodicSpendCounter 
from backend.apps.adminpanel.serializers import ProjectOverviewSerializer
from backend.apps.store.models import PaymentHistory
from backend.apps.store.serializers import PaymentHistorySerializer
from rest_framework import generics

class ProjectOverviewView(APIView):
    def get(self, request, space_id):
        existing_records = ProjectOverview.objects.filter(space_id=space_id)

        if not existing_records.exists():

            cards_count = TinkAccount.objects.filter(space_id=space_id).count()

            accounts_count = TinkAccount.objects.filter(space_id=space_id).count()
            categories_count = Category.objects.filter(space_id=space_id).count() 
            goals_count = Goal.objects.filter(space_id=space_id).count() 
            periods_count = PeriodicSpendCounter.objects.filter(space_id=space_id).count()

            structures_count = accounts_count + categories_count + goals_count + periods_count

            storage_data_count = (
                HistoryExpense.objects.filter(space_id=space_id).count() +
                HistoryIncome.objects.filter(space_id=space_id).count() +
                HistoryTransfer.objects.filter(space_id=space_id).count()
            ) * 0.003

            records = [
                {
                    "assets": "cards",
                    "data": cards_count,
                    "price": cards_count * 0.7,
                },
                {
                    "assets": "structures",
                    "data": structures_count,
                    "price": structures_count * 0.03,
                },
                {
                    "assets": "storage data",
                    "data": storage_data_count,
                    "price": max(round(storage_data_count, 1), 0.1),
                },
            ]
            
            for record in records:
                ProjectOverview.objects.create(
                    space_id=space_id,
                    assets=record["assets"],
                    data=record["data"],
                    price=record["price"],
                    updated_date=now(),
                )
            existing_records = ProjectOverview.objects.filter(space_id=space_id)

        else:
            for record in existing_records:
                if record.assets == "cards":
                    new_data = TinkAccount.objects.filter(space_id=space_id).count()
                    new_price = new_data * 0.7
                elif record.assets == "structures":
                    new_data = (TinkAccount.objects.filter(space_id=space_id).count() +
                                Category.objects.filter(space_id=space_id).count() +
                                Goal.objects.filter(space_id=space_id).count() +
                                PeriodicSpendCounter.objects.filter(space_id=space_id).count())
                    new_price = new_data * 0.03
                elif record.assets == "storage data":
                    new_data = (
                        HistoryExpense.objects.filter(space_id=space_id).count() +
                        HistoryIncome.objects.filter(space_id=space_id).count() +
                        HistoryTransfer.objects.filter(space_id=space_id).count()
                    ) * 0.003
                    new_price = max(round(new_data, 1), 0.1)

                if record.data != new_data or record.price != new_price:
                    record.data = new_data
                    record.price = new_price
                    record.updated_date = now()
                    record.save()

        serializer = ProjectOverviewSerializer(existing_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


