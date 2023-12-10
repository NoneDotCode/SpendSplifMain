from rest_framework.permissions import IsAuthenticated

from apps.customuser.models import CustomUser
from apps.customuser.serializers import CustomUserSerializer
from apps.settings import permissions

from rest_framework import generics


class EditCustomUser(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsOwnerOrReadOnly,
                          IsAuthenticated]

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return CustomUser.objects.filter(pk=pk)

