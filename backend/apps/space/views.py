from django.db import transaction
from rest_framework import generics, status
from rest_framework.response import Response

from backend.apps.customuser.models import CustomUser
from backend.apps.space.models import Space, MemberPermissions
from backend.apps.space.serializers import SpaceSerializer, AddAndRemoveMemberSerializer, MemberPermissionsSerializer
from backend.apps.space.permissions import (IsSpaceOwner, IsSpaceMember, IsMemberAndOwnerOrCanRemoveMember,
                                            CanAddMembers)


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
    permission_classes = (IsSpaceMember, IsSpaceOwner,)

    def get_queryset(self):
        return Space.objects.filter(pk=self.kwargs.get("pk"))


class DeleteSpace(generics.RetrieveDestroyAPIView):
    serializer_class = SpaceSerializer
    permission_classes = (IsSpaceMember, IsSpaceOwner,)

    def get_queryset(self):
        return Space.objects.filter(pk=self.kwargs.get("pk"))


class AddMemberToSpace(generics.GenericAPIView):
    serializer_class = AddAndRemoveMemberSerializer
    permission_classes = (IsSpaceMember and (IsSpaceOwner or CanAddMembers))

    @staticmethod
    def put(request, *args, **kwargs):
        print(f"Active permission classes: {AddMemberToSpace.permission_classes}")
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

        # Add user to the space.
        space.members.add(user)

        # Return success answer
        return Response({"success": "User successfully added to the space."}, status=status.HTTP_200_OK)


class RemoveMemberFromSpace(generics.GenericAPIView):
    serializer_class = AddAndRemoveMemberSerializer
    permission_classes = (IsMemberAndOwnerOrCanRemoveMember,)

    @staticmethod
    def put(request, *args, **kwargs):
        space_pk = kwargs.get("pk")
        user_pk = request.data.get("user_pk")

        try:
            space = Space.objects.get(pk=space_pk)
            user = CustomUser.objects.get(pk=user_pk)
        except (Space.DoesNotExist, CustomUser.DoesNotExist):
            return Response({"error": "Space or user not found."}, status=status.HTTP_404_NOT_FOUND)

        if user not in space.members.all():
            return Response({"error": "User is not member of the space already."},
                            status=status.HTTP_400_BAD_REQUEST)

        space.members.remove(user)

        return Response({"success": "User successfully removed from the space."}, status=status.HTTP_200_OK)


class MemberPermissionsEdit(generics.RetrieveUpdateAPIView):
    serializer_class = MemberPermissionsSerializer
    permission_classes = ()

    def get_queryset(self):
        return MemberPermissions.objects.filter(space_id=self.kwargs.get("space_pk"),
                                                member_id=self.kwargs.data.get("member_id"))

    def update(self, request, *args, **kwargs):
        # Defining which permissions need to edit
        permissions_to_update = request.data

        # Getting object MemberPermissions
        instance = MemberPermissions.objects.get(space_id=kwargs.get("pk"),
                                                 member_id=kwargs.get("member_id"))

        # Изменяем переданные права
        for key, value in permissions_to_update.items():
            setattr(instance, key, value)

        # Save edited permissions
        instance.save()

        # Return successfully response
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
