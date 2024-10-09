from rest_framework.permissions import BasePermission

class IsEmployee(BasePermission):
    def has_permission(self, request, *args, **kwargs):
        return "employee" in request.user.roles