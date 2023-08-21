from django.db import transaction
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from rest_framework.reverse import reverse_lazy
from rest_framework.utils import json

from apps.account.models import Account
from apps.category.models import Category
from apps.category.serializer import CategorySerializer
from apps.history.models import History


class CreateCategory(generics.CreateAPIView):
    serializer_class = CategorySerializer


class AllCategory(generics.ListAPIView):
    model = Category
    login_url = reverse_lazy('token_obtain_pair')
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.all()


class EditCategory(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


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
    History.objects.create(number=data['number'],
                           currency=acc.currency,
                           comment=data['comment'],
                           from_acc=acc.title,
                           to_cat=cat.title,
                           father_space_id=acc.father_space_id)
    return redirect(reverse_lazy('my_categories'))
