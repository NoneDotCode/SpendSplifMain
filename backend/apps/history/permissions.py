from rest_framework.permissions import BasePermission

from backend.apps.account.permissions import IsSpaceOwner
from backend.apps.space.models import Space
from backend.apps.history.models import HistoryExpense, HistoryIncome  # Предполагаем, что эти модели существуют


class CanEditHistory(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get("space_pk")
        history_pk = view.kwargs.get("pk")
        space = Space.objects.get(pk=space_pk)

        try:
            # Проверяем, существует ли запись истории и принадлежит ли она данному пространству
            history = HistoryExpense.objects.get(pk=history_pk) or HistoryIncome.objects.get(pk=history_pk)
        except (HistoryExpense.DoesNotExist, HistoryIncome.DoesNotExist):
            return False

        if history.father_space_id != space_pk:
            return False

        return (IsSpaceOwner().has_permission(request, view) or
                space.members.filter(id=user.id, memberpermissions__edit_history=True).exists())


class CanDeleteHistory(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get("space_pk")
        history_pk = view.kwargs.get("pk")
        space = Space.objects.get(pk=space_pk)

        try:
            # Проверяем, существует ли запись истории и принадлежит ли она данному пространству
            history = HistoryExpense.objects.get(pk=history_pk) or HistoryIncome.objects.get(pk=history_pk)
        except (HistoryExpense.DoesNotExist, HistoryIncome.DoesNotExist):
            return False

        if history.father_space_id != space_pk:
            return False

        return (IsSpaceOwner().has_permission(request, view) or
                space.members.filter(id=user.id, memberpermissions__delete_history=True).exists())