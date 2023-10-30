import json

from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.account.models import Account
from apps.account.permissions import IsOwnerOfFatherSpace, IsInRightSpace, IsOwnerOfSpace
from apps.account.serializers import AccountSerializer

from apps.category.models import Category
from apps.category.serializers import CategorySerializer

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


