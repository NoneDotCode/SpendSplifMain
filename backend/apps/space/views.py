from rest_framework import generics

from backend.apps.account.models import Account
from backend.apps.category.models import Category
from backend.apps.customuser.models import CustomUser
from backend.apps.customuser.serializers import CustomUserSerializer
from backend.apps.notifications.models import Notification
from backend.apps.space.models import Space, MemberPermissions, SpaceBackup
from backend.apps.space.serializers import SpaceSerializer, SpaceListSerializer, AddAndRemoveMemberSerializer, MemberPermissionsSerializer
from backend.apps.space.permissions import (IsSpaceOwner, IsSpaceMember, CanAddMembers, CanRemoveMembers,
                                            CanEditMembers, UserRolePermision)
from backend.apps.account import permissions
from rest_framework.response import Response
from rest_framework import status

from backend.apps.converter.utils import convert_currencies

from backend.apps.goal.models import Goal

from backend.apps.total_balance.models import TotalBalance

from django.db import transaction

from rest_framework.permissions import IsAuthenticated
import random
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from rest_framework.views import APIView
from backend.apps.space.permissions import IsSpaceMember, IsSpaceOwner
from backend.apps.account.permissions import IsSpaceMember as IsSpaceMemberAcc
from backend.apps.converter.utils import convert_number_to_letter


class CreateSpace(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, UserRolePermision)
    serializer_class = SpaceSerializer

    def perform_create(self, serializer):
        user_space_counter = Space.objects.filter(members=self.request.user).count()
        highest_role = self.request.user.roles[0]
        if highest_role == "free" or highest_role == "standard":
            return Response("Error: you can't create spaces because your role is free or standard", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if user_space_counter >= 5:
            return Response("Error: you can't create more than 5 spaces", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
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
                father_space=space,
                color="#FF9800",
                icon="Donut"
            )

            Category.objects.create(
                title="Home",
                spent=0,
                father_space=space,
                color="#FF5050",
                icon="Home"
            )

            Account.objects.create(
                title="Cash",
                balance=0,
                currency=self.request.data.get("currency"),
                father_space=space
            )

            TotalBalance.objects.create(balance=0, father_space=space)


class ListOfSpaces(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SpaceListSerializer

    def get_queryset(self):
        return Space.objects.filter(members=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ListOfUsersInSpace(generics.ListAPIView):
    permission_classes = (permissions.IsSpaceMember,)
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        space = Space.objects.get(pk=self.kwargs.get("space_pk"))
        request_user = self.request.user

        members = list(space.members.all())

        if request_user in members:
            members.remove(request_user)

        members.insert(0, request_user)

        return members


class EditSpace(generics.RetrieveUpdateAPIView):
    serializer_class = SpaceSerializer
    permission_classes = (IsSpaceMember, IsSpaceOwner, UserRolePermision)

    def get_queryset(self):
        return Space.objects.filter(pk=self.kwargs.get("pk"))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
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
            total_balance.balance=convert_currencies(amount=total_balance.balance,
                                                     from_currency=instance.currency,
                                                     to_currency=currency)
            total_balance.save()
        for goal in Goal.objects.filter(father_space=instance):
            goal.collected = convert_currencies(amount=goal.collected,
                                                from_currency=instance.currency,
                                                to_currency=currency)
            goal.save()
        instance.currency = currency
        instance.title = request.data.get("title")
        instance.save()
        return Response(serializer.data)


class DeleteSpace(generics.RetrieveDestroyAPIView):
    serializer_class = SpaceSerializer
    permission_classes = (IsSpaceMember, IsSpaceOwner, UserRolePermision)

    def get_queryset(self):
        return Space.objects.filter(pk=self.kwargs.get("pk"))


class AddMemberToSpace(generics.GenericAPIView):
    serializer_class = AddAndRemoveMemberSerializer
    permission_classes = (IsSpaceMember & (IsSpaceOwner | CanAddMembers),)

    @staticmethod
    def put(request, *args, **kwargs):
        space_pk = kwargs.get("pk")
        user_email = request.data.get("user_email", )
        space = Space.objects.get(pk=space_pk)

        try:
            user = CustomUser.objects.get(email=user_email)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)

        # Check if user is not yet member of the space.
        if user in space.members.all():
            return Response({"error": "User is member of the space already."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Add user to the space.
        space.members.add(user)

        notif_message = f"The user ~{user.username}#{user.tag}~ has been added to the ~{space.title}~ space."
        Notification.objects.create(message=notif_message, who_can_view=space.members.all(), importance="Medium")

        # Return success answer
        return Response({"success": "User successfully added to the space."}, status=status.HTTP_200_OK)


class RemoveMemberFromSpace(generics.GenericAPIView):
    serializer_class = AddAndRemoveMemberSerializer
    permission_classes = (IsSpaceMember & (IsSpaceOwner | CanRemoveMembers),)

    @staticmethod
    def put(request, *args, **kwargs):
        space_pk = kwargs.get("pk")
        user_email = request.data.get("user_email", )
        space = Space.objects.get(pk=space_pk)

        try:
            user = CustomUser.objects.get(email=user_email)
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

    def get_object(self):
        space_id = self.kwargs.get("pk")
        member_id = self.kwargs.get("member_id")
        result_object = MemberPermissions.objects.get(space_id=space_id, member_id=member_id)
        return result_object

    def update(self, request, *args, **kwargs):
        space_id = kwargs.get("pk")
        member_id = kwargs.get("member_id")
        space = Space.objects.get(pk=space_id)

        try:
            user = CustomUser.objects.get(pk=member_id)
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


class SpaceBackupSimulator:
    def __init__(self, space):
        self.space = space

    def generate_backup(self, backup_date):
        accounts = self.generate_accounts()
        categories = self.generate_categories()

        return SpaceBackup.objects.create(
            father_space=self.space,
            date=backup_date,
            accounts=accounts,
            categories=categories
        )

    def generate_accounts(self):
        accounts = []
        for i in range(random.randint(2, 5)):
            balance = Decimal(random.uniform(0, 10000)).quantize(Decimal('0.01'))
            account = {
                'id': i + 1,
                'title': f'Account {i + 1}',
                'balance': float(balance),
                'balance_converted': convert_number_to_letter(balance),
                'currency': random.choice(['USD', 'EUR', 'GBP']),
                'included_in_total_balance': random.choice([True, False]),
                'spend': float(Decimal(random.uniform(0, 1000)).quantize(Decimal('0.01'))),
                'income': float(Decimal(random.uniform(0, 2000)).quantize(Decimal('0.01'))),
            }
            account['formatted_spend'] = convert_number_to_letter(account['spend'])
            account['formatted_income'] = convert_number_to_letter(account['income'])
            accounts.append(account)
        return accounts

    def generate_categories(self):
        categories = []
        for i in range(random.randint(3, 7)):
            spent = Decimal(random.uniform(0, 500)).quantize(Decimal('0.01'))
            limit = Decimal(random.uniform(float(spent), 1000)).quantize(Decimal('0.01'))
            category = {
                'id': i + 1,
                'title': f'Category {i + 1}',
                'spent': float(spent),
                'limit': float(limit),
                'limit_formatted': convert_number_to_letter(limit),
                'color': f'#{random.randint(0, 0xFFFFFF):06x}',
                'icon': random.choice(['Home', 'Food', 'Transport', 'Entertainment']),
                'spent_percentage': f"{round((spent / limit) * 100)}%"
            }
            categories.append(category)
        return categories


class SpaceBackupListView(APIView):
    permission_classes = [IsAuthenticated, IsSpaceMemberAcc]

    @staticmethod
    def post(request, *args, **kwargs):
        space_id = kwargs.get('space_pk')
        try:
            space = Space.objects.get(id=space_id)
        except Space.DoesNotExist:
            return Response({"error": "Space not found"}, status=status.HTTP_404_NOT_FOUND)

        year = request.data.get('year')
        month = request.data.get('month')

        if year and month:
            try:
                year = int(year)
                month = int(month)
            except ValueError:
                return Response({"error": "Year and month must be integers"}, status=status.HTTP_400_BAD_REQUEST)

            backups = SpaceBackup.objects.filter(
                father_space=space,
                date__year=year,
                date__month=month
            ).order_by('-date')
        else:
            return Response({"error": "Year and month are required"}, status=status.HTTP_400_BAD_REQUEST)

        if not backups.exists():
            return Response({"message": "No backups found for the specified period"}, status=status.HTTP_404_NOT_FOUND)

        latest_backup = backups.first()
        backup_data = {
            'id': latest_backup.id,
            'date': latest_backup.date,
            'accounts': latest_backup.accounts,
            'categories': latest_backup.categories
        }

        return Response(backup_data)


class SpaceBackupSimulatorView(APIView):
    permission_classes = (IsSpaceMemberAcc,)

    def post(self, request, *args, **kwargs):
        space_id = kwargs.get('space_pk')
        num_backups = request.data.get('num_backups', 7)  # По умолчанию создаем 3 бэкапа

        try:
            space = Space.objects.get(id=space_id)
        except Space.DoesNotExist:
            return Response({"error": "Space not found"}, status=status.HTTP_404_NOT_FOUND)

        simulator = SpaceBackupSimulator(space)
        created_backups = []

        for i in range(num_backups):
            backup_date = timezone.now().date() - timedelta(days=30 * i)
            backup = simulator.generate_backup(backup_date)
            created_backups.append({
                'id': backup.id,
                'date': backup.date,
            })

        return Response({
            "message": f"Successfully created {num_backups} backups",
            "backups": created_backups
        }, status=status.HTTP_201_CREATED)
