from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy

from apps.space.models import Space
from apps.space.serializers import SpaceSerializer


class CreateSpace(generics.CreateAPIView):
    serializer_class = SpaceSerializer


class AllSpaces(generics.ListAPIView):
    model = Space
    login_url = reverse_lazy("token_obtain_pair")
    serializer_class = SpaceSerializer

    def get_queryset(self):
        return Space.objects.filter(owner_id=self.request.user.id)


# class EditSpace(ModelViewSet):
#     def put(request):
#         pk = request.data.get('pk')
#         space = Space.objects.get(pk=pk)
#         space.title = request.data.get('title')
#         space.save()
#         serializer = SpaceSerializer
#         return Response(serializer.data, status=status.HTTP_200_OK)


class EditSpace(generics.ListAPIView, generics.UpdateAPIView):
    serializer_class = SpaceSerializer

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        return Space.objects.filter(pk=pk)

    def put(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        space = Space.objects.get(pk=pk)
        space.title = request.data.get("title")
        space.save()
        serializer = SpaceSerializer(space)
        return Response(serializer.data, status=status.HTTP_200_OK)
