import ast
import os
import sys

from django_celery_beat.models import PeriodicTask, CrontabSchedule

from rest_framework import generics, status
from django.core.exceptions import ValidationError
from rest_framework.response import Response

from backend.apps.account.models import Account
from backend.apps.account.permissions import IsSpaceMember

from backend.apps.category.models import Category

from backend.apps.spend.permissions import SpendPermission, CanCreatePeriodicSpends, CanDeletePeriodicSpends, \
    CanEditPeriodicSpends
from backend.apps.spend.serializers import PeriodicSpendCreateSerializer, PeriodicSpendEditSerializer, SpendSerializer
from backend.apps.spend.models import PeriodicSpendCounter

from backend.apps.converter.utils import convert_currencies

from backend.apps.history.models import HistoryExpense

from backend.apps.total_balance.models import TotalBalance

from backend.apps.space.models import Space

import json
import inflect

p = inflect.engine()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class SpendView(generics.GenericAPIView):
    serializer_class = SpendSerializer
    permission_classes = (SpendPermission,)

    @staticmethod
    def put(request, *args, **kwargs):
        space_pk = kwargs.get('space_pk')
        space = Space.objects.get(pk=space_pk)
        account = Account.objects.get(pk=request.data.get("account_pk"))
        amount = request.data.get('amount')
        try:
            1 / amount
        except (TypeError, ZeroDivisionError):
            return Response({"error": "You should put amount bigger than 0."}, status=status.HTTP_400_BAD_REQUEST)
        category_pk = request.data.get("category_pk")
        if amount > int(account.balance):
            return Response({"error": "Is not enough money on the balance."}, status=status.HTTP_400_BAD_REQUEST)
        account.balance -= amount
        account.save()

        category = None
        if category_pk:
            category = Category.objects.filter(pk=category_pk).first()
            to_currency = space.currency
            category.spent += convert_currencies(amount=amount,
                                                 from_currency=account.currency,
                                                 to_currency=to_currency)
            category.save()

        total_balance = TotalBalance.objects.get(father_space_id=space_pk)

        total_balance.balance -= convert_currencies(amount=amount,
                                                    from_currency=account.currency,
                                                    to_currency=space.currency)
        total_balance.save()

        comment = request.data.get("comment")
        if comment is None:
            comment = ""

        from_acc_data = {
            'id': account.id,
            'title': account.title,
            'balance': float(account.balance),
            'currency': account.currency,
            'included_in_total_balance': account.included_in_total_balance,
            'father_space': account.father_space.id
        }

        to_cat_data = None
        if category:
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
            comment=comment,
            from_acc=from_acc_data,
            to_cat=to_cat_data if to_cat_data else None,
            father_space_id=space_pk,
            amount_in_default_currency=convert_currencies(amount=amount,
                                                          from_currency=account.currency,
                                                          to_currency=space.currency),
            new_balance=total_balance.balance
        )
        return Response({"success": "Expense successfully completed."}, status=status.HTTP_200_OK)


class PeriodicSpendCreateView(generics.GenericAPIView):
    serializer_class = PeriodicSpendCreateSerializer
    permission_classes = (IsSpaceMember, CanCreatePeriodicSpends)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account_pk = serializer.validated_data.get('account_pk')
        category_pk = serializer.validated_data.get('category_pk')
        amount = serializer.validated_data.get('amount')
        title = serializer.validated_data.get('title')
        hour = serializer.validated_data.get("hour")
        minute = serializer.validated_data.get("minute")
        day_of_week = serializer.validated_data.get("day_of_week")
        day_of_month = serializer.validated_data.get("day_of_month")
        month_of_year = serializer.validated_data.get("month_of_year")
        space_pk = kwargs.get("space_pk")

        try:
            space = Space.objects.get(pk=space_pk)
        except Space.DoesNotExist:
            return Response({"error": "Space does not exist."}, status=status.HTTP_404_NOT_FOUND)

        periodic_spends_count = PeriodicSpendCounter.objects.filter(user=request.user).count()
        highest_role = request.user.roles[0]

        if (highest_role == "premium" or highest_role == "premium/pre") and periodic_spends_count >= 20:
            return Response({"error": "You can't create more than 20 periodic spends with a premium role."},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif (highest_role == "standard" or highest_role == "standard/pre") and periodic_spends_count >= 10:
            return Response({"error": "You can't create more than 10 periodic spends with a standard role."},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif highest_role == "free" and periodic_spends_count >= 5:
            return Response({"error": "You can't create more than 5 periodic spends with a free role."},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if amount <= 0:
            return Response({"error": "The amount must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)

        schedule, created = CrontabSchedule.objects.get_or_create(hour=hour,
                                                                  minute=minute,
                                                                  day_of_week=day_of_week,
                                                                  day_of_month=day_of_month,
                                                                  month_of_year=month_of_year)

        try:
            PeriodicTask.objects.create(
                crontab=schedule,
                name=f"periodic_spend_{request.user.id}_{title}",
                task="backend.apps.spend.tasks.periodic_spend",
                args=json.dumps([account_pk, category_pk, space_pk, float(amount), title, space.currency])
            )
        except ValidationError as e:
            return Response({"error": f"Failed to create task: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        PeriodicSpendCounter.objects.create(user=request.user, father_space=space, title=title)
        return Response({"success": "Periodic task successfully created."}, status=status.HTTP_200_OK)


class PeriodicSpendDeleteView(generics.GenericAPIView):
    permission_classes = (IsSpaceMember, CanDeletePeriodicSpends)

    @staticmethod
    def delete(request, *args, **kwargs):
        periodic_spend_pk = kwargs.get("pk")
        task = PeriodicTask.objects.get(pk=periodic_spend_pk)
        task.delete()
        return Response({"success": "Periodic spend successfully deleted."}, status=status.HTTP_200_OK)


class PeriodicSpendEditView(generics.GenericAPIView):
    serializer_class = PeriodicSpendEditSerializer
    permission_classes = (IsSpaceMember, CanEditPeriodicSpends)

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account_pk = serializer.validated_data.get('account_pk')
        category_pk = serializer.validated_data.get('category_pk')
        amount = serializer.validated_data.get('amount')
        title = serializer.validated_data.get('title')
        hour = serializer.validated_data.get("hour")
        minute = serializer.validated_data.get("minute")
        day_of_week = serializer.validated_data.get("day_of_week")
        day_of_month = serializer.validated_data.get("day_of_month")
        month_of_year = serializer.validated_data.get("month_of_year")

        periodic_spend_pk = kwargs.get("pk")
        task = PeriodicTask.objects.get(pk=periodic_spend_pk)
        task_args = ast.literal_eval(task.args)
        space = Space.objects.get(pk=task_args[2])
        new_args = [account_pk, category_pk, kwargs.get("space_pk"), amount, title, space.currency]
        for i in range(len(new_args)):
            if new_args[i] is None:
                new_args[i] = task_args[i]
        task.args = f"{new_args}"
        task.save()
        task.name = f"periodic_spend_{request.user.id}_{new_args[4]}"
        task_crontab = task.crontab
        task_crontab_dict = {"hour": task_crontab.hour,
                             "minute": task_crontab.minute,
                             "day_of_week": task_crontab.day_of_week,
                             "day_of_month": task_crontab.day_of_month,
                             "month_of_year": task_crontab.month_of_year}
        crontab_vars = {"hour": hour, "minute": minute, "day_of_week": day_of_week, "day_of_month": day_of_month,
                        "month_of_year": month_of_year}
        for i in crontab_vars:
            if crontab_vars[i] is None:
                crontab_vars[i] = task_crontab_dict[i]
        schedule, created = CrontabSchedule.objects.get_or_create(hour=crontab_vars["hour"],
                                                                  minute=crontab_vars["minute"],
                                                                  day_of_week=crontab_vars["day_of_week"],
                                                                  day_of_month=crontab_vars["day_of_month"],
                                                                  month_of_year=crontab_vars["month_of_year"])
        task.crontab = schedule
        task.save()
        return Response({"success": "Periodic Spend successfully edited."}, status=status.HTTP_200_OK)


class PeriodicSpendsGetView(generics.GenericAPIView):
    permission_classes = (IsSpaceMember,)

    @staticmethod
    def get(request, *args, **kwargs):
        def key(task):
            try:
                check1 = f"periodic_spend_{request.user.id}" in task.name
                check2 = ast.literal_eval(task.args)[2] == kwargs.get("space_pk")
                return check1 and check2
            except (ValueError, KeyError, IndexError):
                return False

        periodic_spends_list = list(filter(key, PeriodicTask.objects.all()))
        result = []
        for spend in periodic_spends_list:
            spend_args = ast.literal_eval(spend.args)
            crontab = spend.crontab

            if crontab.day_of_week == "*" and crontab.day_of_month != "*":
                spend_sch_str = "Every month"
                spend_sch_int = p.ordinal(p.number_to_words(int(crontab.day_of_month)))
            elif crontab.day_of_week != "*" and crontab.day_of_month == "*":
                spend_sch_str = "Every week"

                try:
                    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    spend_sch_int = days[int(crontab.day_of_week) - 1]
                except (ValueError, IndexError):
                    continue
            else:
                continue

            account = Account.objects.get(pk=spend_args[0])
            category = Category.objects.get(pk=spend_args[1])
            temp = {
                "id": spend.id,
                "title": spend.name.replace(f"periodic_spend_{request.user.id}_", ""),
                "account": account.title,
                "category": category.title,
                "category_icon": category.icon,
                "currency": account.currency,
                "amount": spend_args[3],
                "schedule": spend_sch_str,
                "day": spend_sch_int
            }
            result.append(temp)
        return Response(result, status=status.HTTP_200_OK)
