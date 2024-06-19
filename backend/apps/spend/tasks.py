from decimal import Decimal

from celery import shared_task

from backend.apps.account.models import Account
from backend.apps.category.models import Category
from backend.apps.converter.utils import convert_currencies
from backend.apps.history.models import HistoryExpense
from backend.apps.total_balance.models import TotalBalance


@shared_task(bind=True)
def periodic_spend(self, account_pk, category_pk, space_pk, amount, title, to_currency):
    account = Account.objects.get(pk=account_pk)
    category = Category.objects.get(pk=category_pk)
    if amount > int(account.balance):
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
