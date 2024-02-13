from drf_multiple_model.views import ObjectMultipleModelAPIView

from backend.apps.history.models import HistoryIncome, HistoryExpense
from backend.apps.history.serializers import HistoryIncomeSerializer, HistoryExpenseSerializer

from backend.apps.account.permissions import IsSpaceMember


class HistoryView(ObjectMultipleModelAPIView):
    permission_classes = (IsSpaceMember,)

    def get_querylist(self):
        space_pk = self.kwargs["space_pk"]
        return [
            {"queryset": HistoryIncome.objects.filter(father_space_id=space_pk), "serializer_class":
                HistoryIncomeSerializer},
            {"queryset": HistoryExpense.objects.filter(father_space_id=space_pk), "serializer_class":
                HistoryExpenseSerializer}
        ]
