from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import os
from openai import OpenAI

from backend.apps.account.permissions import IsSpaceMember, IsSpaceOwner

from backend.apps.category.models import Category
from backend.apps.category.permissions import (CanCreateCategories, CanEditCategories,
                                               CanDeleteCategories)
from backend.apps.category.serializers import CategorySerializer
from backend.apps.space.models import Space

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
        if user_categories_counter >= 126 and highest_role == "business_lic":
            return Response("Error: you can't create more than 126 categories because your role is Business license", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif user_categories_counter >= 126 and highest_role == "business_plan" :
            return Response("Error: you can't create more than 126 categories because your role is Business plan", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif user_categories_counter >= 3 and highest_role == "free":
            return Response("Error: you can't create more than 3 categories because your role is free", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
       
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


os.environ["OPENAI_API_KEY"] = "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"

class CategorizeExpense(APIView):
    def post(self, request, *args, **kwargs):
        space_pk = kwargs.get('space_pk')
        category_name = request.data.get('category_name')
        amount = request.data.get('amount')
        counterpart_name = request.data.get('counterpart_name')
        purpose = request.data.get('purpose')
        currency = request.data.get('currency')
        
        # Получаем пространство (спейс) и проверяем доступ пользователя
        space = Space.objects.filter(pk=space_pk, members=request.user).first()
        if not space:
            return Response({"detail": "You do not have permission to access this space."}, status=status.HTTP_403_FORBIDDEN)
        
        # Получаем все категории из спейса
        categories = Category.objects.filter(father_space=space).values('id', 'title')
        if not categories:
            return Response({"detail": "No categories found in this space."}, status=status.HTTP_404_NOT_FOUND)

        # Формируем список названий категорий для запроса к OpenAI
        category_names = ", ".join([cat['title'] for cat in categories])

        # Формируем запрос к OpenAI
        prompt = (
            f"The following are categories for expenses: {category_names}. "
            f"An expense has been made with the following details: "
            f"Category Name: {category_name}, Amount: {amount} {currency}, "
            f"Counterpart Name: {counterpart_name}, Purpose: {purpose}. "
            f"Which category does this expense most likely fall into? "
            f"Please respond with the exact category name."
        )

        # Инициализация клиента OpenAI
        client = OpenAI() 

        try:
            # Запрос к OpenAI
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that classifies expenses into predefined categories."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50
            )
            
            # Получаем название категории от OpenAI
            suggested_category_name = response.choices[0].message.content.strip()
            
            # Ищем категорию по названию
            category = next((cat for cat in categories if cat['title'] == suggested_category_name), None)

            print("НОВЫЙ ЗАПРОС")
            print(prompt)
            print(suggested_category_name)
            print(category)

            # Если категория не найдена, выбираем первую категорию из списка
            if not category:
                category = categories[0]
            
            # Возвращаем только ID категории
            return Response({"category_id": category['id']})
        
        except Exception as e: 
            category = categories[0]
            return Response({"category_id": category['id']})
        