from django.db import transaction
from django.shortcuts import redirect

from rest_framework import generics
from rest_framework.decorators import permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse_lazy
from rest_framework.utils import json

from apps.account.models import Account
from apps.account.permissions import IsOwnerOfFatherSpace, IsInRightSpace, IsOwnerOfSpace

from apps.category.models import Category
from apps.category.serializer import CategorySerializer, SpendSerializer

from apps.space.models import Space


class CreateCategory(generics.CreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsOwnerOfSpace,)

    def create(self, request, *args, **kwargs):
        space_pk = self.kwargs.get('space_pk')
        space = get_object_or_404(Space, pk=space_pk)
        request.data['father_space'] = space.pk
        request.data['minus'] = 0
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


# @permission_classes([IsOwnerOfSpace])
# @transaction.atomic
# def spend(request):
#     data = json.loads(request.body)
#     number = data['number']
#     acc = Account.objects.get(pk=data['pk_acc'])
#     acc.balance -= number
#     cat = Category.objects.get(pk=data['pk_cat'])
#     cat.minus += number
#     acc.save()
#     cat.save()
#     return redirect(reverse_lazy('my_categories'))


class SpendView(generics.UpdateAPIView):
    serializer_class = SpendSerializer
    permission_classes = (IsOwnerOfSpace, IsInRightSpace)

    def get_object(self):
        return Account.objects.get(pk=self.kwargs['from'])

    def perform_update(self, serializer):
        number = serializer.validated_data['amount']
        acc = self.get_object()
        acc.balance -= number
        cat = Category.objects.get(pk=self.kwargs['to'])
        cat.minus += number
        acc.save()
        cat.save()
