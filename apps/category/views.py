from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.account.models import Account
from apps.account.permissions import IsOwnerOfFatherSpace, IsInRightSpace, IsOwnerOfSpace
from apps.account.serializers import AccountSerializer

from apps.category.models import Category
from apps.category.permissions import SpendPermission
from apps.category.serializers import CategorySerializer

from apps.space.models import Space

from apps.history.models import HistoryExpense

from apps.total_balance.models import TotalBalance

from apps.converter.utils import convert_currencies


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

    @staticmethod
    def put(request, *args, **kwargs):
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
        comment = request.data.get("comment")
        if comment is None:
            comment = ""
        HistoryExpense.objects.create(
            amount=amount,
            currency=account.currency,
            comment=comment,
            from_acc=account.title,
            to_cat=category.title,
            father_space_id=space_pk
        )
        total_balance = TotalBalance.objects.filter(father_space_id=space_pk)
        if total_balance:
            total_balance[0].balance -= convert_currencies(amount=amount,
                                                           from_currency=account.currency,
                                                           to_currency=total_balance[0].currency)
            total_balance[0].save()
        return Response({"success": "Expense successfully completed."}, status=status.HTTP_200_OK)
