from rest_framework import permissions

from apps.space.models import Space

from apps.account.models import Account


class IsOwnerOfFatherSpace(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return Space.objects.get(pk=obj.father_space_id).members.filter()


class IsInRightSpace(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.parser_context['kwargs'].get('space_pk') == obj.father_space_id


class IsOwnerOfSpace(permissions.BasePermission):

    def has_permission(self, request, view):
        return Space.objects.get(pk=request.parser_context['kwargs'].get('space_pk')).members == request.user


class IncomePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get('space_pk')
        account_pk = view.kwargs.get('pk')
        try:
            account = Account.objects.get(pk=account_pk)
            space = Space.objects.get(pk=space_pk)
        except (Account.DoesNotExist, Space.DoesNotExist):
            return False
        return space.owner == user and account.father_space == space
