from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, permissions
from backend.apps.banners.models import Banner
import random
from rest_framework import generics, permissions, status
from backend.apps.banners.serializers import BannerSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class BannerUploadView(generics.CreateAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if "sponsor" not in request.user.roles:
            return Response({"detail": "You do not have permission to upload banners."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = BannerSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class RandomBannerView(generics.RetrieveAPIView):
    serializer_class = BannerSerializer

    def get_object(self):
        active_banners = Banner.objects.filter(is_active=True)
        banner = random.choice(active_banners)
        banner.views += 1

        if banner.goal_view is not None and banner.views >= banner.goal_view:
            banner.is_active = False

        banner.save()
        return banner
    

class BannerClickView(generics.GenericAPIView):
    queryset = Banner.objects.all()

    def post(self, request, *args, **kwargs):
        banner_id = kwargs.get('pk')
        banner = Banner.objects.get(pk=banner_id)
        banner.clicks += 1

        if banner.goal_click is not None and banner.clicks >= banner.goal_click:
            banner.is_active = False

        banner.save()
        return JsonResponse({'message': 'Click recorded'}, status=200)