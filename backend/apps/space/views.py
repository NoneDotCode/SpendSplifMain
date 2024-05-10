from django.db import transaction
from rest_framework import generics

from backend.apps.account.models import Account
from backend.apps.category.models import Category
from backend.apps.customuser.models import CustomUser
from backend.apps.customuser.serializers import CustomUserSerializer
from backend.apps.space.models import Space, MemberPermissions
from backend.apps.space.serializers import SpaceSerializer, SpaceListSerializer, AddAndRemoveMemberSerializer, MemberPermissionsSerializer
from backend.apps.space.permissions import (IsSpaceOwner, IsSpaceMember, CanAddMembers, CanRemoveMembers,
                                            CanEditMembers)
from backend.apps.account import permissions
from rest_framework.response import Response
from rest_framework import status

from backend.apps.converter.utils import convert_currencies

from backend.apps.goal.models import Goal

from backend.apps.total_balance.models import TotalBalance

from django.db import transaction


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

            # Create two default categories for the newly created space
            Category.objects.create(
                title="Food",
                limit=1000,
                spent=0,
                father_space=space
            )

            Category.objects.create(
                title="Home",
                spent=0,
                father_space=space
            )

            Account.objects.create(
                title="Cash",
                balance=0,
                currency=self.request.data.get("currency"),
                father_space=space
            )


class ListOfSpaces(generics.ListAPIView):
    serializer_class = SpaceListSerializer

    def get_queryset(self):
        return Space.objects.filter(members=self.request.user)


class ListOfUsersInSpace(generics.ListAPIView):
    permission_classes = (permissions.IsSpaceMember,)
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        space = Space.objects.get(pk=self.kwargs.get("space_pk"))
        return space.members


class EditSpace(generics.RetrieveUpdateAPIView):
    serializer_class = SpaceSerializer
    permission_classes = (IsSpaceMember, IsSpaceOwner,)

    def get_queryset(self):
        return Space.objects.filter(pk=self.kwargs.get("pk"))
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        currency = self.request.data.get("currency")
        for category in Category.objects.filter(father_space=instance):
            category.spent = convert_currencies(amount=category.spent,
                                                from_currency=instance.currency,
                                                to_currency=currency)
            category.save()
        total_balance = TotalBalance.objects.get(father_space=instance)
        if total_balance:
            total_balance.save(balance=convert_currencies(amount=instance.balance,
                                                        from_currency=instance.currency,
                                                        to_currency=currency))
        for goal in Goal.objects.filter(father_space=instance):
            goal.collected = convert_currencies(amount=goal.collected,
                                                from_currency=instance.currency,
                                                to_currency=currency)
            goal.save()
        return Response(serializer.data)


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
            user = CustomUser.objects.get(pk=user_pk)
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
