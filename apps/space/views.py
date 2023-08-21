from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy

from .serializers import SpaceSerializer
from .models import Space


class CreateSpace(generics.CreateAPIView):
    serializer_class = SpaceSerializer


class AllSpaces(generics.ListAPIView):
    serializer_class = SpaceSerializer

    def get_queryset(self):
        return Space.objects.filter(owner_id=self.request.user.id)


class EditSpace(generics.ListAPIView, generics.UpdateAPIView):
    serializer_class = SpaceSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Space.objects.filter(pk=pk)
