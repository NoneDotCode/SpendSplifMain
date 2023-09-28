from celery import shared_task

from apps.category.models import Category


@shared_task(bind=True)
def clear_all_spent(self):
    all_categories = Category.objects.all()
    for category in all_categories:
        category.spent = 0
        category.save()
    return "All spent cleared"
