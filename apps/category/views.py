from django.db import transaction
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics
from rest_framework.reverse import reverse_lazy
from rest_framework.utils import json

from apps.account.models import Account
from apps.account.permissions import IsOwnerOfFatherSpace, IsInRightSpace

from apps.category.models import Category
from apps.category.serializer import CategorySerializer


class CreateCategory(generics.CreateAPIView):
    serializer_class = CategorySerializer


class ViewCategory(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(father_space_id=self.kwargs.get("space_pk"))


class EditCategory(generics.RetrieveUpdateAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsOwnerOfFatherSpace, IsInRightSpace)

    def get_queryset(self):
        return Category.objects.filter(father_space_id=self.kwargs.get("space_pk"))


class DeleteCategory(generics.RetrieveDestroyAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(pk=self.kwargs.get('pk'))


@csrf_exempt
@transaction.atomic
def spend(request):
    data = json.loads(request.body)
    number = data['number']
    acc = Account.objects.get(pk=data['pk_acc'])
    acc.balance -= number
    cat = Category.objects.get(pk=data['pk_cat'])
    cat.minus += number
    acc.save()
    cat.save()
    return redirect(reverse_lazy('my_categories'))
