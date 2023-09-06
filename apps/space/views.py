from rest_framework import generics


from apps.space.models import Space
from apps.space.serializers import SpaceSerializer
from apps.space.permissions import IsOwner


class CreateSpace(generics.CreateAPIView):
    serializer_class = SpaceSerializer


class ViewSpace(generics.ListAPIView):
    serializer_class = SpaceSerializer

    def get_queryset(self):
        return Space.objects.filter(owner_id=self.request.user.id)


class EditSpace(generics.RetrieveUpdateAPIView):
    serializer_class = SpaceSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        return Space.objects.filter(pk=pk)


class DeleteSpace(generics.RetrieveDestroyAPIView):
    serializer_class = SpaceSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        return Space.objects.filter(pk=pk)
