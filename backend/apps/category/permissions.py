from rest_framework import permissions

from backend.apps.account.models import Account
from backend.apps.account.permissions import IsSpaceOwner
from backend.apps.category.models import Category

from backend.apps.space.models import Space


class CanCreateCategories(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space = Space.objects.get(pk=view.kwargs.get("space_pk"))

        return space.members.filter(id=user.id, memberpermissions__create_categories=True).exists()


class CanEditCategories(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get("space_pk")
        category_pk = view.kwargs.get("pk")
        space = Space.objects.get(pk=space_pk)

        try:
            category = Account.objects.get(pk=category_pk)
        except Category.DoesNotExist:
            return False

        if category.father_space_id != space_pk:
            return False

        return (IsSpaceOwner().has_permission(request, view) or
                space.members.filter(id=user.id, memberpermissions__edit_categories=True).exists())


class CanDeleteAccounts(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get("space_pk")
        category_pk = view.kwargs.get("pk")
        space = Space.objects.get(pk=space_pk)

        try:
            category = Account.objects.get(pk=category_pk)
        except Category.DoesNotExist:
            return False

        if category.father_space_id != space_pk:
            return False

        return (IsSpaceOwner().has_permission(request, view) or
                space.members.filter(id=user.id, memberpermissions__delete_categories=True).exists())
