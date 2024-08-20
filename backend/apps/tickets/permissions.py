from django.core.exceptions import ObjectDoesNotExist

from rest_framework.permissions import BasePermission

from backend.apps.tickets.models import TicketChat 
from backend.apps.customuser.models import CustomUser

class IsEmployee(BasePermission):
    def has_permission(self, request, *args, **kwargs):
        return "employee" in request.user.roles
    
class IsBusiness(BasePermission):
    def has_permission(self, request, *args, **kwargs):
        return "business" in request.user.roles
    
class IsMemeberOfChat(BasePermission):
    def has_permission(self, request, view):
        try:
            owner_1 = CustomUser.objects.get(id=view.kwargs.get('owner_1_id'))
            owner_2 = CustomUser.objects.get(id=view.kwargs.get('owner_2_id'))
            chat =  TicketChat.objects.get(user=owner_1, employee_id=owner_2)
            owners = (owner_1, owner_2)
            if not chat or request.user not in owners:
                return False
        except ObjectDoesNotExist:
            return False
        return True 