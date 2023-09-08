from apps.customuser.models import CustomUser
from apps.customuser.serializers import CustomUserSerializer
from apps.settings import permissions
from apps.settings.permissions import IsOwnerOrReadOnly

from rest_framework import generics


class EditCustomUser(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsOwnerOrReadOnly]

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return CustomUser.objects.filter(pk=pk)

