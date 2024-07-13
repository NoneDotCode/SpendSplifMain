from decimal import Decimal

from celery import shared_task

from backend.apps.account.models import Account
from backend.apps.category.models import Category
from backend.apps.converter.utils import convert_currencies
from backend.apps.history.models import HistoryExpense
from backend.apps.notifications.models import Notification
from backend.apps.space.models import Space
from backend.apps.total_balance.models import TotalBalance


@shared_task(bind=True)
def periodic_spend(self, account_pk, category_pk, space_pk, amount, title, to_currency):
    space = Space.objects.get(pk=space_pk)
    try:
        account = Account.objects.get(pk=account_pk)
    except Account.DoesNotExist:
        notif_message = f"Recurring spend {title} in space {space.title} was not completed because account was deleted."
        Notification.objects.create(message=notif_message, who_can_view=space.members.all(), importance="Important")
        return "Expense did not complete successfully"
    try:
        category = Category.objects.get(pk=category_pk)
    except Category.DoesNotExist:
        notif_message = f"Recurring spend {title} in space {space.title} was not completed because category was deleted."
        Notification.objects.create(message=notif_message, who_can_view=space.members.all(), importance="Important")
        return "Expense did not complete successfully"
    if amount > int(account.balance):
        notif_message = (f"Recurring spend {title} in space {space.title} was not completed because you have not enough"
                         f"money on the balance {account.title}.")
        Notification.objects.create(message=notif_message, who_can_view=space.members.all(), importance="Important")
        return f"It is not enough money on the balance for {title} spend."
    account.balance -= Decimal(amount)
    account.save()
    category.spent += convert_currencies(amount=amount,
                                         from_currency=account.currency,
                                         to_currency=to_currency)
    category.save()
    total_balance = TotalBalance.objects.filter(father_space_id=space_pk)
    if total_balance:
        total_balance[0].balance -= convert_currencies(amount=amount,
                                                       from_currency=account.currency,
                                                       to_currency=to_currency)
        total_balance[0].save()
    comment = title

    from_acc_data = {
        'id': account.id,
        'title': account.title,
        'balance': float(account.balance),
        'currency': account.currency,
        'included_in_total_balance': account.included_in_total_balance,
        'father_space': account.father_space.id
    }

    to_cat_data = {
        'id': category.id,
        'title': category.title,
        'spent': float(category.spent),
        'limit': float(category.limit) if category.limit else None,
        'color': category.color,
        'icon': category.icon,
        'father_space': category.father_space.id
    }

    HistoryExpense.objects.create(
        amount=amount,
        currency=account.currency,
        amount_in_default_currency=convert_currencies(from_currency=account.currency,
                                                      amount=amount,
                                                      to_currency=to_currency),
        comment=comment,
        from_acc=from_acc_data,
        to_cat=to_cat_data,
        periodic_expense=True,
        father_space_id=space_pk,
        new_balance=total_balance[0].balance if total_balance else 0
    )

    return "Expense successfully completed."
