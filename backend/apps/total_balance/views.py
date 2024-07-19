from rest_framework import generics
from backend.apps.total_balance.models import TotalBalance
from backend.apps.total_balance.serializers import TotalBalanceSerializer

from backend.apps.account.permissions import IsSpaceMember


class ViewTotalBalance(generics.ListAPIView):
    serializer_class = TotalBalanceSerializer
    permission_classes = (IsSpaceMember,)

    def get_queryset(self):
        return TotalBalance.objects.filter(father_space_id=self.kwargs["space_pk"])
