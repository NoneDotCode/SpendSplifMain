from rest_framework import generics
from rest_framework.generics import get_object_or_404

from backend.apps.account.permissions import IsSpaceMember, IsSpaceOwner

from backend.apps.category.models import Category
from backend.apps.category.permissions import (CanCreateCategories, CanEditCategories,
                                               CanDeleteCategories)
from backend.apps.category.serializers import CategorySerializer
from backend.apps.category.utils import get_next_order
from backend.apps.space.models import Space

from rest_framework.response import Response
from rest_framework import status


class CreateCategory(generics.CreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsSpaceMember & (IsSpaceOwner | CanCreateCategories),)

    def create(self, request, *args, **kwargs):
        space_pk = self.kwargs.get('space_pk')
        space = get_object_or_404(Space, pk=space_pk)
        request.data['father_space'] = space.pk
        request.data['spent'] = 0
        if request.data.get('order') is None:
            try:
                request.data["order"] = get_next_order(space_pk)
            except (Exception,):
                return Response({'error': "You have too many categories"}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)


class ViewCategory(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsSpaceMember,)

    def get_queryset(self):
        return Category.objects.filter(father_space_id=self.kwargs.get("space_pk"))


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
