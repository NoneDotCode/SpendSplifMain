from rest_framework import permissions

from apps.space.models import Space


class IsOwnerOfFatherSpace(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return Space.objects.get(pk=obj.father_space_id).owner == request.user


class IsInRightSpace(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.parser_context['kwargs'].get("space_pk") == obj.father_space_id
