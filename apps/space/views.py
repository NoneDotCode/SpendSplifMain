from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import generics
from rest_framework.reverse import reverse_lazy

from .serializers import SpaceSerializer
from .models import Space


class CreateSpace(generics.CreateAPIView):
    serializer_class = SpaceSerializer


class AllSpaces(generics.ListAPIView):
    model = Space
    login_url = reverse_lazy('token_obtain_pair')
    serializer_class = SpaceSerializer

    def get_queryset(self):
        return Space.objects.filter(owner_id=self.request.user.id)
