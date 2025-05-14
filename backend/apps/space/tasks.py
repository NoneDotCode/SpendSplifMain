from celery import shared_task
from django.utils import timezone
import json
from decimal import Decimal
from datetime import timedelta

from backend.apps.account.serializers import AccountSerializer
from backend.apps.category.serializers import CategorySerializer
from backend.apps.space.models import Space, SpaceBackup
from backend.apps.total_balance.models import TotalBalance
from backend.apps.total_balance.serializers import TotalBalanceSerializer


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


@shared_task
def create_space_backup():
    spaces = Space.objects.all()
    for space in spaces:
        backup_date = timezone.now().date() - timedelta(days=1)  

        accounts = json.loads(json.dumps(
            AccountSerializer(space.account_set.all(), many=True).data,
            cls=DecimalEncoder
        ))
        categories = json.loads(json.dumps(
            CategorySerializer(space.category_set.all(), many=True).data,
            cls=DecimalEncoder
        ))

        total_balance = TotalBalance.objects.filter(father_space=space).first()
        total_balance_data = None
        if total_balance:
            total_balance_data = json.loads(json.dumps(
                TotalBalanceSerializer(total_balance).data,
                cls=DecimalEncoder
            ))

        SpaceBackup.objects.create(
            father_space=space,
            date=backup_date,
            accounts=accounts,
            categories=categories,
            total_balance=total_balance_data
        )

    return "Backups created successfully for all spaces"