from django.db import transaction
from rest_framework import generics, status
from rest_framework.response import Response

from apps.customuser.models import CustomUser
from apps.messenger.models import SpaceGroup
from apps.space.models import Space, MemberPermissions
from apps.space.serializers import SpaceSerializer, AddMemberToSpaceSerializer
from apps.space.permissions import IsSpaceOwner, IsMemberOfSpace, IsMemberOrOwnerOrCanAddMember


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


class ListOfSpaces(generics.ListAPIView):
    serializer_class = SpaceSerializer

    def get_queryset(self):
        return Space.objects.filter(members=self.request.user)


class EditSpace(generics.RetrieveUpdateAPIView):
    serializer_class = SpaceSerializer
    permission_classes = (IsMemberOfSpace, IsSpaceOwner,)

    def get_queryset(self):
        return Space.objects.filter(pk=self.kwargs.get("pk"))


class DeleteSpace(generics.RetrieveDestroyAPIView):
    serializer_class = SpaceSerializer
    permission_classes = (IsMemberOfSpace, IsSpaceOwner,)

    def get_queryset(self):
        return Space.objects.filter(pk=self.kwargs.get("pk"))


class AddMemberToSpace(generics.GenericAPIView):
    serializer_class = AddMemberToSpaceSerializer
    permission_classes = (IsMemberOrOwnerOrCanAddMember,)

    def put(self, request, *args, **kwargs):
        space_pk = kwargs.get("pk")
        user_pk = request.data.get("user_pk")

        try:
            space = Space.objects.get(pk=space_pk)
            user = CustomUser.objects.get(pk=user_pk)
        except (Space.DoesNotExist, CustomUser.DoesNotExist):
            return Response({"error": "Space or user not found."},
                            status=status.HTTP_404_NOT_FOUND)

        # Check if user is not yet member of the space.
        if user in space.members.all():
            return Response({"error": "User is member of the space already."},
                            status=status.HTTP_400_BAD_REQUEST)

        if not SpaceGroup.objects.filter(father_space=space_pk).exists():
            space_group = SpaceGroup(father_space_id=space_pk)
            space_group.save()

        # Add user to the space.
        space.members.add(user)

        # Return success answer
        return Response({"success": "User successfully added to the space."}, status=status.HTTP_200_OK)
