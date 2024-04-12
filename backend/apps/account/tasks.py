from celery import shared_task

from datetime import datetime, timedelta

from backend.apps.customuser.models import CustomUser

@shared_task
def delete_not_verify_users():
    time_to_verify_account = datetime.now() - timedelta(hours=24)

    not_verify_users = CustomUser.objects.filter(is_active=False, date_joined__gte=time_to_verify_account)
    
    for user in not_verify_users:
        user.delete()