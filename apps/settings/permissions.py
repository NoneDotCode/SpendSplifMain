from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    # пользователи могут редактировать только свои собственные объекты

    def has_object_permission(self, request, view, obj):

        # разрешить запись только владельцу объекта
        if obj.pk == request.user.pk:
            return True

        return False
