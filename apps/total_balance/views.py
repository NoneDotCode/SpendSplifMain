from rest_framework import generics
from rest_framework.response import Response

from apps.total_balance.models import TotalBalance
from apps.total_balance.serializers import TotalBalanceSerializer


from apps.converter.utils import convert_currencies

from apps.category.models import Category


class ViewTotalBalance(generics.ListAPIView):
    serializer_class = TotalBalanceSerializer
    permission_classes = ()

    def get_queryset(self):
        return TotalBalance.objects.filter(father_space_id=self.kwargs["space_pk"])


class EditTotalBalance(generics.RetrieveUpdateAPIView):
    serializer_class = TotalBalanceSerializer
    permission_classes = ()

    # def get_queryset(self):
    #     return TotalBalance.objects.filter(father_space_id=self.kwargs["space_pk"])

    def get_object(self):
        return TotalBalance.objects.get(father_space_id=self.kwargs.get("space_pk"))

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        currency = request.data.get("currency")
        if currency == instance.currency:
            return Response({"error": "you changed nothing"})
        for category in Category.objects.filter(father_space_id=instance.father_space_id):
            category.spent = convert_currencies(amount=category.spent,
                                                from_currency=instance.currency,
                                                to_currency=currency)
            category.save()
        serializer.save(balance=convert_currencies(amount=instance.balance,
                                                   from_currency=instance.currency,
                                                   to_currency=currency),
                        currency=currency)
        return Response(serializer.data)
