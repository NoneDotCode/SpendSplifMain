from django.http import JsonResponse
from rest_framework import generics

from apps.customuser.models import CustomUser
from apps.messenger.models import DmMessage, DmChat
from apps.messenger.serializers import DmMessageSerializer
from rest_framework.response import Response
from rest_framework import status
from apps.messenger.serializers import DmChatSerializer


class CreateChatView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        owner_1_username = request.data.get('owner_1')
        owner_2 = request.user

        try:
            owner_1 = CustomUser.objects.get(username=owner_1_username)
            if not CustomUser.objects.filter(username=owner_2.username).exists():
                return Response({"error": "Owner 2 does not exist"},
                                status=status.HTTP_404_NOT_FOUND)

            request.data['owner_1'] = owner_1.username  # Use username instead of id
            request.data['owner_2'] = owner_2.username  # Use username instead of id

            serializer = DmChatSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"error": "Owner 1 does not exist"},
                            status=status.HTTP_404_NOT_FOUND)


class ChatView(generics.GenericAPIView):
    def get(self, request, owner_1_id, owner_2_id):
        chat = DmChat.objects.filter(owner_1_id=owner_1_id, owner_2_id=owner_2_id).first()
        if not chat:
            return JsonResponse({'error': 'Chat not found'}, status=404)
        messages = DmMessage.objects.filter(father_chat=chat)
        response = {
            'messages': [{'sender': message.sender.username, 'text': message.text} for message in messages]
        }
        return JsonResponse(response)

    def post(self, request, owner_1_id, owner_2_id):
        chat = DmChat.objects.filter(owner_1_id=owner_1_id, owner_2_id=owner_2_id).first()
        serializer = DmMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, father_chat_id=chat.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
