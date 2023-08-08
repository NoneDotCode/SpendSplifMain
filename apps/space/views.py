from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy

from .serializers import SpaceSerializer
from .models import Space


class CreateSpace(generics.CreateAPIView):

    serializer_class = SpaceSerializer


class AllSpaces(LoginRequiredMixin, generics.ListAPIView):
    model = Space
    login_url = reverse_lazy('token_obtain_pair')

    def get_queryset(self):
        return Space.objects.filter(owner_id=self.request.user.id)

    serializer_class = SpaceSerializer
    get_queryset = get_queryset



