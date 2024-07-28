from rest_framework import generics
from rest_framework.generics import get_object_or_404

from backend.apps.account.permissions import IsSpaceMember, IsSpaceOwner

from backend.apps.category.models import Category
from backend.apps.category.permissions import (CanCreateCategories, CanEditCategories,
                                               CanDeleteCategories)
from backend.apps.category.serializers import CategorySerializer
from backend.apps.space.models import Space

from rest_framework.response import Response
from rest_framework import status

import logging

logger = logging.getLogger(__name__)


class CreateCategory(generics.CreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsSpaceMember & (IsSpaceOwner | CanCreateCategories),)

    def create(self, request, *args, **kwargs):
        space_pk = self.kwargs.get('space_pk')
        space = get_object_or_404(Space, pk=space_pk)

        user_categories_counter = Category.objects.filter(father_space=space).count()
        highest_role = self.request.user.roles[0]
        if user_categories_counter >= 100 and highest_role == "premium":
            return Response("Error: you can't create more than 100 categories because your role is premium", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif user_categories_counter >= 50 and highest_role == "standard" :
            return Response("Error: you can't create more than 50 categories because your role is standard", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif user_categories_counter >= 25 and highest_role == "free":
            return Response("Error: you can't create more than 25 categories because your role is free", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
       
        data = request.data.copy()
        data['father_space'] = space.pk
        data['spent'] = 0

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ViewCategory(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsSpaceMember,)

    def get_queryset(self):
        return Category.objects.filter(father_space_id=self.kwargs.get("space_pk")).order_by('pk')


class EditCategory(generics.RetrieveUpdateAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsSpaceMember, CanEditCategories)

    def get_queryset(self):
        return Category.objects.filter(father_space_id=self.kwargs.get("space_pk"))


class DeleteCategory(generics.RetrieveDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = (CanDeleteCategories,)

    def get_queryset(self):
        return Category.objects.filter(pk=self.kwargs.get('pk'))
