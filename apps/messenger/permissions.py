from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission

from apps.messenger.models import DmChat
from apps.space.models import Space


class IsMemberOfSpace(BasePermission):
    def has_object_permission(self, request, view, obj):
        print(isinstance(obj, Space))
        if isinstance(obj, Space):
            print(request.user)
            print(obj.members.all())
            return request.user in obj.members
        return request.user in obj.space.members.all()


class IsMemberOfDmChat(BasePermission):
    def has_permission(self, request, view):
        owner_1_id = view.kwargs.get('owner_1_id')
        owner_2_id = view.kwargs.get('owner_2_id')
        chat = DmChat.objects.filter(owner_1_id=owner_1_id, owner_2_id=owner_2_id).first()
        owners = [owner_1_id, owner_2_id]
        if not chat or request.user.id not in owners:
            return False
        return True
