from rest_framework import generics
from apps.total_balance.models import TotalBalance
from apps.total_balance.serializers import TotalBalanceSerializer


class TotalBalanceView(generics.ListAPIView):
    serializer_class = TotalBalanceSerializer

    def get_queryset(self):
        return TotalBalance.objects.filter(father_space_id=self.request.data.get('father_space_id'))
