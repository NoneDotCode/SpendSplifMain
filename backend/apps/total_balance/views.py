from rest_framework import generics, status
from rest_framework.response import Response

from backend.apps.total_balance.models import TotalBalance
from backend.apps.total_balance.serializers import TotalBalanceSerializer

from backend.apps.account.permissions import IsSpaceMember, IsSpaceOwner

from backend.apps.converter.utils import convert_currencies

from backend.apps.category.models import Category
from backend.apps.goal.models import Goal


class ViewTotalBalance(generics.ListAPIView):
    serializer_class = TotalBalanceSerializer
    permission_classes = (IsSpaceMember,)

    def get_queryset(self):
        return TotalBalance.objects.filter(father_space_id=self.kwargs["space_pk"])
