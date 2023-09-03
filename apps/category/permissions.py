from rest_framework import permissions

from apps.account.models import Account

from apps.category.models import Category

from apps.space.models import Space


class SpendPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get('space_pk')
        from_pk = view.kwargs.get('from')
        category_pk = view.kwargs.get('pk')
        try:
            account = Account.objects.get(pk=from_pk)
            category = Category.objects.get(pk=category_pk)
            space = Space.objects.get(pk=space_pk)
        except (Account.DoesNotExist, Category.DoesNotExist, Space.DoesNotExist):
            return False
        return space.owner == user and account.father_space == space and category.father_space == space
