from rest_framework import generics
from rest_framework.response import Response

from apps.converter.models import Currency
from apps.converter.utils import update_currencies


class ConvertCurrencyView(generics.RetrieveAPIView):
    def get(self, request, **kwargs):
        from_currency = self.request.data.get('from_currency')
        to_currency = self.request.data.get('to_currency')
        amount = self.request.data.get('amount')

        euro_amount = amount / Currency.objects.get(iso_code=from_currency).euro
        converted_amount = round(euro_amount * Currency.objects.get(iso_code=to_currency).euro, 2)

        update_currencies()
        return Response({'converted_amount': converted_amount})
