from rest_framework import generics
from rest_framework.generics import get_object_or_404
import openai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from backend.apps.account.permissions import IsSpaceMember, IsSpaceOwner

from backend.apps.category.models import Category
from backend.apps.category.permissions import (CanCreateCategories, CanEditCategories,
                                               )
from backend.apps.category.serializers import CategorySerializer
from backend.apps.space.models import Space


class CreateCategory(generics.CreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsSpaceMember & (IsSpaceOwner | CanCreateCategories),)

    def create(self, request, *args, **kwargs):
        space_pk = self.kwargs.get('space_pk')
        space = get_object_or_404(Space, pk=space_pk)
        request.data['father_space'] = space.pk
        request.data['spent'] = 0
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
    permission_classes = ()

    def get_queryset(self):
        return Category.objects.filter(pk=self.kwargs.get('pk'))




openai.api_key = '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'
class CategorizeExpense(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        space_pk = kwargs.get('space_pk')
        store_name = request.data.get('store_name')
        
        space = Space.objects.filter(pk=space_pk, members=request.user).first()
        if not space:
            return Response({"detail": "You do not have permission to access this space."}, status=403)
        
        categories = Category.objects.filter(father_space=space).values_list('title', flat=True)
        category_names = ", ".join(categories)

        
        prompt = f"The following are categories for expenses: {category_names}. The store '{store_name}' is a type of store where you can buy various items. Which category does the expense from this store most likely fall into? Please respond with the exact category name or 'other' if none match."

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that classifies expenses into predefined categories."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50
            )
            
            category = response['choices'][0]['message']['content'].strip()
        
            if category not in categories:
                category = "other"
        
            return Response({"category": category})
        
        except openai.error.OpenAIError as e:
            return Response({"detail": str(e)}, status=500)