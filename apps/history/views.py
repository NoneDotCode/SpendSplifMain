from rest_framework import generics

from apps.history.models import History
from apps.history.serializers import HistorySerializer


class ViewHistory(generics.ListAPIView):
    serializer_class = HistorySerializer
    model = History

    def get_queryset(self):
        return History.objects.filter(father_space_id=self.request.data.get())
