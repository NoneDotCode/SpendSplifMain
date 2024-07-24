from celery import shared_task
from django.utils import timezone

from backend.apps.account.serializers import AccountSerializer
from backend.apps.category.serializers import CategorySerializer
from backend.apps.space.models import Space, SpaceBackup


@shared_task
def create_space_backup():
    spaces = Space.objects.all()
    for space in spaces:
        backup_date = timezone.now().date()

        accounts = AccountSerializer(space.account_set.all(), many=True).data

        categories = CategorySerializer(space.category_set.all(), many=True).data

        SpaceBackup.objects.create(
            father_space=space,
            date=backup_date,
            accounts=accounts,
            categories=categories
        )

    return "Backups created successfully for all spaces"
