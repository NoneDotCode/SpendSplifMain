from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from backend.apps.converter.utils import convert_currencies


class ConvertCurrencyView(generics.RetrieveAPIView):
    permission_classes = [AllowAny,]

    def post(self, request, **kwargs):
        from_currency = self.request.data.get('from_currency')
        to_currency = self.request.data.get('to_currency')
        amount = self.request.data.get('amount')

        converted_amount = convert_currencies(from_currency=from_currency, to_currency=to_currency, amount=amount)

        return Response({'Converted successfully:': f"{amount} {from_currency} = {converted_amount} {to_currency}"})
