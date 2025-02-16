from django.core.exceptions import ObjectDoesNotExist

from rest_framework.permissions import BasePermission

from backend.apps.tickets.models import TicketChat 
from backend.apps.customuser.models import CustomUser

class IsEmployee(BasePermission):
    def has_permission(self, request, *args, **kwargs):
        return "employee" in request.user.roles


class IsBusiness(BasePermission):
    def has_permission(self, request, *args, **kwargs):
        # Список ролей, которые мы проверяем
        business_roles = {"business_plan", "business_member_plan", "business_lic", "business_member_lic"}
        
        # Получаем роли пользователя (это массив строк)
        user_roles = set(request.user.roles)
        
        # Проверяем, есть ли пересечение между ролями пользователя и бизнес-ролями
        return bool(user_roles & business_roles)


class IsMemberOfChat(BasePermission):
    def has_permission(self, request, view):
        try:
            chat_id = view.kwargs.get('chat_id')
            if not chat_id:
                return False
                
            chat = TicketChat.objects.get(id=chat_id)
            user = request.user
            
            # Check if the requesting user is either the user or employee in the chat
            return user == chat.user or user == chat.employee
            
        except ObjectDoesNotExist:
            return False
        except AttributeError:
            return False

    def has_object_permission(self, request, view, obj):
        # Additional object-level permission check if needed
        user = request.user
        return user == obj.user or user == obj.employee
    