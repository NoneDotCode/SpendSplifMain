from django.db import transaction
from rest_framework import generics


from apps.space.models import Space, MemberPermissions
from apps.space.serializers import SpaceSerializer
from apps.space.permissions import IsSpaceOwner


class CreateSpace(generics.CreateAPIView):
    serializer_class = SpaceSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            # Save the space instance
            space = serializer.save()

            # Create a MemberPermissions instance setting the current user as the owner
            MemberPermissions.objects.create(
                member=self.request.user,
                space=space,
                owner=True
            )


class ViewSpace(generics.ListAPIView):
    serializer_class = SpaceSerializer

    def get_queryset(self):
        return Space.objects.filter(owner_id=self.request.user.id)


class EditSpace(generics.RetrieveUpdateAPIView):
    serializer_class = SpaceSerializer
    permission_classes = (IsSpaceOwner,)

    def get_queryset(self):
        pk = self.kwargs.get("space_pk")
        return Space.objects.filter(pk=pk)


class DeleteSpace(generics.RetrieveDestroyAPIView):
    serializer_class = SpaceSerializer
    permission_classes = (IsSpaceOwner,)

    def get_queryset(self):
        pk = self.kwargs.get("space_pk")
        return Space.objects.filter(pk=pk)
