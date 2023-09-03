from django.db import transaction
from django.shortcuts import redirect

from rest_framework import generics, status
from rest_framework.decorators import permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework.utils import json

from apps.account.models import Account
from apps.account.permissions import IsOwnerOfFatherSpace, IsInRightSpace, IsOwnerOfSpace
from apps.account.serializers import AccountSerializer

from apps.category.models import Category
from apps.category.serializers import CategorySerializer
from apps.category.permissions import SpendPermission

from apps.space.models import Space


class CreateCategory(generics.CreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsOwnerOfSpace,)

    def create(self, request, *args, **kwargs):
        space_pk = self.kwargs.get('space_pk')
        space = get_object_or_404(Space, pk=space_pk)
        request.data['father_space'] = space.pk
        request.data['spent'] = 0
        return super().create(request, *args, **kwargs)


class ViewCategory(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsOwnerOfSpace,)

    def get_queryset(self):
        return Category.objects.filter(father_space_id=self.kwargs.get("space_pk"))


class EditCategory(generics.RetrieveUpdateAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsOwnerOfFatherSpace, IsInRightSpace)

    def get_queryset(self):
        return Category.objects.filter(father_space_id=self.kwargs.get("space_pk"))


class DeleteCategory(generics.RetrieveDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsOwnerOfFatherSpace, IsInRightSpace)

    def get_queryset(self):
        return Category.objects.filter(pk=self.kwargs.get('pk'))


class SpendView(generics.GenericAPIView):

    def get_queryset(self):
        return Account.objects.filter(pk=self.kwargs['from'])

    serializer_class = AccountSerializer
    permission_classes = (SpendPermission,)

    def put(self, request, *args, **kwargs):
        space_pk = kwargs.get('space_pk')
        from_pk = kwargs.get('from')
        try:
            account = Account.objects.get(pk=from_pk)
        except Account.DoesNotExist:
            return Response({"error": "Account didn't found"}, status=status.HTTP_404_NOT_FOUND)
        category_id = kwargs.get('pk')
        amount = request.data.get('amount')
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return Response({"error": "Category didn't found"})
        if amount > account.balance:
            return Response({"error": "Is not enough money on the balance."}, status=status.HTTP_400_BAD_REQUEST)
        account.balance -= amount
        account.save()
        category.spent += amount
        category.save()
        return Response({"success": "Expense successfully completed."}, status=status.HTTP_200_OK)
