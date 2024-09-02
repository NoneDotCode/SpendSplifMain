from rest_framework.permissions import BasePermission

from backend.apps.space.models import Space

class UserRolePermision(BasePermission):
    def has_permission(self, request, view):
        highest_role = request.user.roles[0]
        if "free" == highest_role or "standard" == highest_role:
            return False
        return True

class IsSpaceMember(BasePermission):

    def has_permission(self, request, view):

        try:
            space = Space.objects.get(pk=view.kwargs.get("pk", ))
        except Space.DoesNotExist:
            return False

        if request.user not in space.members.all():
            return False

        return True


class IsSpaceOwner(BasePermission):

    def has_permission(self, request, view):
        space = Space.objects.get(pk=view.kwargs.get("pk", ))

        if not space.memberpermissions_set.filter(member=request.user, owner=True).exists():
            return False

        return True


class CanAddMembers(BasePermission):

    def has_permission(self, request, view):
        space = Space.objects.get(pk=view.kwargs.get("pk", ))

        if not space.memberpermissions_set.filter(member=request.user, add_members=True).exists():
            return False

        return True


class CanRemoveMembers(BasePermission):

    def has_permission(self, request, view):
        space = Space.objects.get(pk=view.kwargs.get("pk", ))

        if not space.memberpermissions_set.filter(member=request.user, remove_members=True).exists():
            return False

        return True


class CanEditMembers(BasePermission):

    def has_permission(self, request, view):
        space = Space.objects.get(pk=view.kwargs.get("pk"))

        if not space.memberpermissions_set.filter(member=request.user, edit_members=True).exists():
            return False

        return True
