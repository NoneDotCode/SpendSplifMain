from rest_framework import generics
from rest_framework.response import Response

from apps.converter.models import Currency
from apps.converter.utils import update_currencies, convert_currencies


class ConvertCurrencyView(generics.RetrieveAPIView):
    def get(self, request, **kwargs):
        from_currency = self.request.data.get('from_currency')
        to_currency = self.request.data.get('to_currency')
        amount = self.request.data.get('amount')

        converted_amount = convert_currencies(from_currency=from_currency, to_currency=to_currency, amount=amount)

        return Response({'converted_amount': converted_amount})
