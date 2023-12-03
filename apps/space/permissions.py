from rest_framework.permissions import BasePermission

from apps.space.models import Space


class IsMemberOfSpace(BasePermission):
    """
    Allows access only to members of the space.
    """

    def has_object_permission(self, request, view, obj):
        # If the object itself is a space, you can check directly
        print(isinstance(obj, Space))
        if isinstance(obj, Space):
            print(request.user)
            print(obj.members.all())
            return request.user in obj.members.all()
        # If the object is related to a space, you'll need to adjust this logic
        # For example, if obj has a space attribute
        return request.user in obj.space.members.all()


class IsSpaceOwner(BasePermission):
    """Allows access only to space owners."""

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__owner=True).exists()


"""Permissions for categories"""


class CanDeleteCategories(BasePermission):
    """
    Allows access only to users who can delete categories in the space
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__delete_categories=True).exists()


class CanEditCategories(BasePermission):
    """
    Allows access only to users who can edit categories in the space.
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__edit_categories=True).exists()


class CanCreateCategories(BasePermission):
    """
    Allows access only to users who can create categories in the space.
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__create_categories=True).exists()


"""Permissions for goals"""


class CanDeleteGoals(BasePermission):
    """
    Allows access only to users who can delete goals in the space
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__delete_goals=True).exists()


class CanEditGoals(BasePermission):
    """
    Allows access only to users who can edit goals in the space.
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__edit_goals=True).exists()


class CanCreateGoals(BasePermission):
    """
    Allows access only to users who can create goals in the space.
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__create_goals=True).exists()


"""Permissions for accounts"""


class CanDeleteAccounts(BasePermission):
    """
    Allows access only to users who can delete accounts in the space
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__delete_accounts=True).exists()


class CanEditAccounts(BasePermission):
    """
    Allows access only to users who can edit accounts in the space.
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__edit_accounts=True).exists()


class CanCreateAccounts(BasePermission):
    """
    Allows access only to users who can create accounts in the space.
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__create_accounts=True).exists()


"""Permissions for managing users"""


class CanRemoveUsers(BasePermission):
    """
    Allows access only to users who can remove users from the space
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__revmove_users=True).exists()


class CanEditUsers(BasePermission):
    """
    Allows access only to users who can edit users in the space.
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__edit_users=True).exists()


class CanAddUsers(BasePermission):
    """
    Allows access only to users who can add users to the space.
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__add_users=True).exists()


"""Permissions for recurring spends."""


class CanDeleteRecurringSpends(BasePermission):
    """
    Allows access only to users who can delete recurring spends in the space
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__delete_recurring_spends=True).exists()


class CanEditRecurringSpends(BasePermission):
    """
    Allows access only to users who can edit recurring spends in the space.
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__edit_recurring_spends=True).exists()


class CanCreateRecurringSpends(BasePermission):
    """
    Allows access only to users who can create recurring spends in the space.
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__create_recurring_spends=True).exists()


"""Permissions for history operations"""


class CanEditHistory(BasePermission):
    """
    Allows access only to users who can edit history records in the space.
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__edit_history=True).exists()


class CanDeleteHistory(BasePermission):
    """
    Allows access only to users who can delete history records in the space.
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__delete_history=True).exists()


"""Permissions for managing users"""


class CanAddBankAccounts(BasePermission):
    """
    Allows access only to users who can add bank accounts to the space
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__add_bank_accounts=True).exists()


class CanRemoveBankAccounts(BasePermission):
    """
    Allows access only to users who can remove bank accounts from the space.
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__remove_bank_accounts=True).exists()


"""Other Permissions"""


class CanSpend(BasePermission):
    """Allows access only to users who can spend in the space."""

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__spend=True).exists()


class CanTransfer(BasePermission):
    """Allow access only to users who can transfer in the space."""

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id, memberpermissions__transfer=True).exists()


class IsMemberOrOwnerOrCanAddMember(BasePermission):
    def has_permission(self, request, view):
        # Логика для проверки, является ли пользователь членом пространства
        if (IsMemberOfSpace().has_permission(request, view) and
                (IsSpaceOwner().has_permission(request, view) or CanAddUsers().has_permission(request, view))):
            return True
        return False
