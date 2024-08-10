from rest_framework.response import Response
from rest_framework import generics, permissions, status
from django.conf import settings


class SubscribePricesView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        data = settings.SUBSCRIBES_DATA
        result = {}
        for subscribe in data:
            for sub_data in data[subscribe]:
                result[f"{subscribe.lower()}_{sub_data}"] = data[subscribe][sub_data]
        return Response(result, status=status.HTTP_200_OK)
