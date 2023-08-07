from rest_framework import generics
from rest_framework.response import Response

from .serializers import SpaceSerializer
from .models import Space


class CreateSpace(generics.CreateAPIView):

    serializer_class = SpaceSerializer
