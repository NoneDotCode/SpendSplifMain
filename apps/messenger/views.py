from django.http import JsonResponse
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from apps.customuser.models import CustomUser
from apps.messenger.models import DmMessage, DmChat, SpaceGroup, MessageGroup
from apps.messenger.permissions import IsMemberOfSpace, IsMemberOfDmChat
from apps.messenger.serializers import DmMessageSerializer, MessageGroupSerializer
from rest_framework.response import Response
from rest_framework import status
from apps.messenger.serializers import DmChatSerializer
from apps.space.models import Space


class CreateChatView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        owner_1_username = request.data.get('owner_1')
        owner_2 = request.user

        try:
            owner_1 = CustomUser.objects.get(username=owner_1_username)
            # Check if both owners exist before proceeding
            if not CustomUser.objects.filter(username=owner_2.username).exists():
                return Response({"error": "Owner 2 does not exist"},
                                status=status.HTTP_404_NOT_FOUND)

            request.data['owner_1'] = owner_1.username
            request.data['owner_2'] = owner_2.username

            serializer = DmChatSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            # If either owner does not exist, return an appropriate error
            return Response({"error": "One or both owners do not exist"},
                            status=status.HTTP_404_NOT_FOUND)


class DmChatView(generics.GenericAPIView):
    permission_classes = [IsMemberOfDmChat, IsAuthenticated]

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
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SpaceChatView(generics.GenericAPIView):

    def get(self, request, group_id):
        group = get_object_or_404(SpaceGroup, id=group_id)
        messages = MessageGroup.objects.filter(father_group=group)
        serializer = MessageGroupSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, group_id):
        group = get_object_or_404(SpaceGroup, id=group_id)
        if request.user not in group.father_space.members.all():
            return Response("User not found in the space", status=status.HTTP_400_BAD_REQUEST)

        request.data['father_group'] = group.id
        serializer = MessageGroupSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(sender=request.user, father_group=group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
