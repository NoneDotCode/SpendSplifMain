from rest_framework.permissions import BasePermission

from apps.customuser.models import CustomUser
from apps.space.models import Space


class IsMemberAndOwnerOrCanRemoveMember(BasePermission):
    def has_permission(self, request, view):
        space_pk = view.kwargs.get("pk")
        user_pk = request.data.get("user_pk")

        try:
            space = Space.objects.get(pk=space_pk)
            CustomUser.objects.get(pk=user_pk)
        except (Space.DoesNotExist, CustomUser.DoesNotExist):
            return False

        if request.user not in space.members.all():
            return False

        # Check if the user is the owner of the space
        if space.memberpermissions_set.filter(member=request.user, owner=True).exists():
            return True

        # Check if the user has permission to remove members from the space
        if not space.memberpermissions_set.filter(member=request.user, remove_users=True).exists():
            return False

        return True


class IsSpaceMember(BasePermission):

    def has_permission(self, request, view):

        try:
            space = Space.objects.get(pk=view.kwargs.get("pk"))
        except Space.DoesNotExist:
            return False

        if request.user not in space.members.all():
            return False


class IsSpaceOwner(BasePermission):

    def has_permission(self, request, view):
        space = Space.objects.get(pk=view.kwargs.get("pk"))

        if not space.memberpermissions_set.filter(member=request.user, owner=True).exists():
            return False

        return True


class CanAddMembers(BasePermission):

    def has_permission(self, request, view):
        space = Space.objects.get(pk=view.kwargs.get("pk"))

        if not space.memberpermissions_set.filter(member=request.user, add_members=True).exists():
            return False

        return True
