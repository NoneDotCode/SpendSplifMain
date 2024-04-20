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
    category.spent += convert_currencies(amount=Decimal(amount),
                                         from_currency=account.currency,
                                         to_currency=to_currency)
    category.save()
    comment = title
    HistoryExpense.objects.create(
        amount=amount,
        currency=account.currency,
        amount_in_default_currency=convert_currencies(from_currency=account.currency,
                                                    amount=amount,
                                                    to_currency=to_currency),
        comment=comment,
        from_acc=account.title,
        to_cat=category.title,
        periodic_expense=True,
        father_space_id=space_pk
    )
    total_balance = TotalBalance.objects.filter(father_space_id=space_pk)
    if total_balance:
        total_balance[0].balance -= convert_currencies(amount=Decimal(amount),
                                                       from_currency=account.currency,
                                                       to_currency=to_currency)
        total_balance[0].save()
    return "Expense successfully completed."
