from celery import shared_task

from apps.account.models import Account

from apps.category.models import Category

from apps.converter.utils import convert_currencies

from apps.history.models import HistoryExpense

from apps.total_balance.models import TotalBalance


@shared_task(bind=True)
def periodic_spend(self, account_pk, category_pk, space_pk, amount, title, to_currency):
    account = Account.objects.get(pk=account_pk)
    category = Category.objects.get(pk=category_pk)
    if amount > int(account.balance):
        return f"Is not enough money on the balance for {title} spend."
    account.balance -= amount
    account.save()
    if TotalBalance.objects.filter(father_space_id=space_pk):
        to_currency = TotalBalance.objects.filter(father_space_id=space_pk)[0].currency
    category.spent += convert_currencies(amount=amount,
                                         from_currency=account.currency,
                                         to_currency=to_currency)
    category.save()
    comment = title
    HistoryExpense.objects.create(
        amount=amount,
        currency=account.currency,
        comment=comment,
        from_acc=account.title,
        to_cat=category.title,
        father_space_id=space_pk
    )
    total_balance = TotalBalance.objects.filter(father_space_id=space_pk)
    if total_balance:
        total_balance[0].balance -= convert_currencies(amount=amount,
                                                       from_currency=account.currency,
                                                       to_currency=total_balance[0].currency)
        total_balance[0].save()
    return "Expense successfully completed."
