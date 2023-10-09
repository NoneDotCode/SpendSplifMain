from drf_multiple_model.views import ObjectMultipleModelAPIView

from apps.history.models import HistoryIncome, HistoryExpense
from apps.history.serializers import HistoryIncomeSerializer, HistoryExpenseSerializer

from apps.account.permissions import IsOwnerOfSpace


class HistoryView(ObjectMultipleModelAPIView):
    permission_classes = (IsOwnerOfSpace,)

    def get_querylist(self):
        space_pk = self.kwargs["space_pk"]
        return [
            {"queryset": HistoryIncome.objects.filter(father_space_id=space_pk), "serializer_class":
                HistoryIncomeSerializer},
            {"queryset": HistoryExpense.objects.filter(father_space_id=space_pk), "serializer_class":
                HistoryExpenseSerializer}
        ]
