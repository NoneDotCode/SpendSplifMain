from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission

from backend.apps.messenger.models import DmChat
from backend.apps.space.models import Space


class IsMemberOfDmChat(BasePermission):
    def has_permission(self, request, view):
        owner_1_id = view.kwargs.get('owner_1_id')
        owner_2_id = view.kwargs.get('owner_2_id')
        chat = DmChat.objects.filter(owner_1_id=owner_1_id, owner_2_id=owner_2_id).first()
        owners = [owner_1_id, owner_2_id]
        if not chat or request.user.id not in owners:
            return False
        return True
