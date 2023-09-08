from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    # пользователи могут редактировать только свои собственные объекты

    def has_object_permission(self, request, view, obj):
        # разрешить чтение всем пользователям

        # get и head запросы всегда разрешены
        if request.method in permissions.SAFE_METHODS:
            return True

        # разрешить запись только владельцу объекта
        if obj.pk == request.user.pk:
            return True

        # разрешить запись только администраторам
        if request.user.is_superuser:
            return True

        return False
