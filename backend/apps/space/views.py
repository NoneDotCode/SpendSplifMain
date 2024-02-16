from django.db import transaction
from rest_framework import generics, status
from rest_framework.response import Response

from backend.apps.customuser.models import CustomUser
from backend.apps.space.models import Space, MemberPermissions
from backend.apps.space.serializers import SpaceSerializer, AddAndRemoveMemberSerializer, MemberPermissionsSerializer
from backend.apps.space.permissions import (IsSpaceOwner, IsSpaceMember, CanAddMembers, CanRemoveMembers,
                                            CanEditMembers)


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
    permission_classes = (IsSpaceMember & (IsSpaceOwner | CanAddMembers),)

    @staticmethod
    def put(request, *args, **kwargs):
        space_pk = kwargs.get("pk")
        user_pk = request.data.get("user_pk", )
        space = Space.objects.get(pk=space_pk)

        try:
            user = CustomUser.objects.get(email=request.user.email)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."},
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
    permission_classes = (IsSpaceMember & (IsSpaceOwner | CanRemoveMembers),)

    @staticmethod
    def put(request, *args, **kwargs):
        space_pk = kwargs.get("pk")
        user_pk = request.data.get("user_pk", )
        space = Space.objects.get(pk=space_pk)

        try:
            user = CustomUser.objects.get(email=request.user.email)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user not in space.members.all():
            return Response({"error": "User is not member of the space already."},
                            status=status.HTTP_400_BAD_REQUEST)
        elif space.memberpermissions_set.filter(member=user, owner=True).exists():
            return Response({"error": "You cannot remove this member from the space"})

        space.members.remove(user)

        return Response({"success": "User successfully removed from the space."}, status=status.HTTP_200_OK)


class MemberPermissionsEdit(generics.RetrieveUpdateAPIView):
    serializer_class = MemberPermissionsSerializer
    permission_classes = (IsSpaceMember & (IsSpaceOwner | CanEditMembers),)

    def get_queryset(self):
        return MemberPermissions.objects.filter(space_id=self.kwargs.get("pk"),
                                                member_id=self.kwargs.get("member_id"))

    def update(self, request, *args, **kwargs):
        space_id = kwargs.get("pk")
        member_id = kwargs.get("member_id")
        space = Space.objects.get(pk=space_id)

        try:
            user = CustomUser.objects.get(email=request.user.email)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user == user:
            return Response({"error": "You cannot edit yourself."}, status=status.HTTP_400_BAD_REQUEST)
        elif space.memberpermissions_set.filter(member=user, owner=True).exists():
            return Response({"error": "You cannot edit this member because it is owner."},
                            status=status.HTTP_400_BAD_REQUEST)

        permissions_to_update = request.data

        try:
            instance = MemberPermissions.objects.get(space_id=space_id, member_id=member_id)
        except MemberPermissions.DoesNotExist:
            return Response({"error": "Something went wrong, check if data is OK."},
                            status=status.HTTP_400_BAD_REQUEST)

        for key, value in permissions_to_update.items():
            setattr(instance, key, value)

        instance.save()

        return Response({'status': 'success'}, status=status.HTTP_200_OK)
