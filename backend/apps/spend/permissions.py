import ast

from django_celery_beat.models import PeriodicTask
from rest_framework import permissions

from backend.apps.account.models import Account
from backend.apps.account.permissions import IsSpaceOwner

from backend.apps.category.models import Category

from backend.apps.space.models import Space


class SpendPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get("space_pk")
        account_pk = request.data.get("account_pk")
        category_pk = request.data.get("category_pk")

        try:
            account = Account.objects.get(pk=account_pk)
            category = Category.objects.get(pk=category_pk)
            space = Space.objects.get(pk=space_pk)
        except (Account.DoesNotExist, Category.DoesNotExist, Space.DoesNotExist):
            return False

        if account.father_space != space or category.father_space != space:
            return print(space, account.father_space, category.father_space)

        return (IsSpaceOwner().has_permission(request, view) or
                space.members.filter(id=user.id, memberpermissions__spend=True).exists())


class CanCreatePeriodicSpends(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get("space_pk")
        account_pk = request.data.get("account_pk")
        category_pk = request.data.get("category_pk")

        try:
            account = Account.objects.get(pk=account_pk)
            category = Category.objects.get(pk=category_pk)
            space = Space.objects.get(pk=space_pk)
        except (Account.DoesNotExist, Category.DoesNotExist, Space.DoesNotExist):
            return False

        if account.father_space != space or category.father_space != space:
            return False

        return (IsSpaceOwner().has_permission(request, view) or
                space.members.filter(id=user.id, memberpermissions__create_recurring_spends=True).exists())


class CanDeletePeriodicSpends(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get("space_pk")
        account_pk = request.data.get("account_pk")
        category_pk = request.data.get("category_pk")
        periodic_spend_pk = view.kwargs.get("pk")

        try:
            task = PeriodicTask.objects.get(pk=periodic_spend_pk)
            account = Account.objects.get(pk=account_pk)
            category = Category.objects.get(pk=category_pk)
            space = Space.objects.get(pk=space_pk)
        except (Account.DoesNotExist, Category.DoesNotExist, Space.DoesNotExist):
            return False

        task_args = ast.literal_eval(task.args)
        father_space = Space.objects.get(pk=task_args[2])

        if account.father_space != space or category.fater_space != space or father_space.pk != space_pk:
            return False

        return (IsSpaceOwner().has_permission(request, view) or
                space.members.filter(id=user.id, memberpermissions__delete_recurring_spends=True).exists())


class CanEditPeriodicSpends(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get("space_pk")
        account_pk = request.data.get("account_pk")
        category_pk = request.data.get("category_pk")
        periodic_spend_pk = view.kwargs.get("pk")

        try:
            task = PeriodicTask.objects.get(pk=periodic_spend_pk)
            account = Account.objects.get(pk=account_pk)
            category = Category.objects.get(pk=category_pk)
            space = Space.objects.get(pk=space_pk)
        except (Account.DoesNotExist, Category.DoesNotExist, Space.DoesNotExist):
            return False

        task_args = ast.literal_eval(task.args)
        father_space = Space.objects.get(pk=task_args[2])

        if account.father_space != space or category.fater_space != space or father_space.pk != space_pk:
            return False

        return (IsSpaceOwner().has_permission(request, view) or
                space.members.filter(id=user.id, memberpermissions__edit_recurring_spends=True).exists())
