from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy

from apps.account.models import Account
from apps.category.models import Category
from apps.category.serializer import CategorySerializer


# class CreateCategory(generics.CreateAPIView):
#     serializer_class = CategorySerializer
#
#     def create_category(request, pk):
#         title = request.POST.get('title')
#         minus = 0
#         limit = request.POST.get('limit')
#         if title == '':
#             raise Exception('Пустое имя сам не поймёшь же...')
#         if limit == '':
#             limit = 0
#         Category.objects.create(title=title, minus=minus, limit=limit, father_space_id=pk)
#         return Response({'status': 'success'}, status=status.HTTP_201_CREATED)


class CreateCategory(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def perform_create(self, serializer):
        serializer.save(father_space_id=self.kwargs['pk'])


class AllCategory(generics.ListAPIView):
    model = Category
    login_url = reverse_lazy('token_obtain_pair')
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.all()


class EditCategory(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
