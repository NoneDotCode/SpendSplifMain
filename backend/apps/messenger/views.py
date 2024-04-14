from django.http import JsonResponse
from rest_framework import generics
from rest_framework.generics import get_object_or_404

from backend.apps.customuser.models import CustomUser
from backend.apps.messenger.models import DmMessage, DmChat, SpaceGroup, MessageGroup
from backend.apps.messenger.permissions import IsMemberOfDmChat
from backend.apps.messenger.serializers import DmMessageSerializer, MessageGroupSerializer
from rest_framework.response import Response
from rest_framework import status

from backend.apps.account.permissions import IsSpaceMember

class CreateChatView(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        try:
            owner_1_data = request.data.get('owner_1').split('#')
            owner_2 = request.user
            owner_1 = CustomUser.objects.get(username=owner_1_data[0], tag=owner_1_data[1])
        except (CustomUser.DoesNotExist,):
            return Response({"error": "One or both owners do not exist"},
                            status=status.HTTP_404_NOT_FOUND)

        if DmChat.objects.filter(owner_1=owner_1, owner_2=owner_2).exists():
            return Response({"error": "Chat already exists"},
                            status=status.HTTP_403_FORBIDDEN)

        DmChat.objects.create(owner_1=owner_1, owner_2=owner_2)
        return Response({
            "success": f"New DmChat with {owner_1.username}#{owner_1.tag}-{owner_2.username}#{owner_2.tag} created"
        },
            status=status.HTTP_200_OK)


class DmChatView(generics.GenericAPIView):
    permission_classes = (IsMemberOfDmChat,)

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
    permission_classes = (IsSpaceMember,)

    @staticmethod
    def get(request, *args, **kwargs):
        group = get_object_or_404(SpaceGroup, father_space_id=kwargs.get("space_pk"))
        messages = MessageGroup.objects.filter(father_group=group)
        serializer = MessageGroupSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def post(request, *args, **kwargs):
        group = get_object_or_404(SpaceGroup, father_space_id=kwargs.get("space_pk"))
        if request.user not in group.father_space.members.all():
            return Response("User not found in the space", status=status.HTTP_400_BAD_REQUEST)

        request.data['father_group'] = group.id
        serializer = MessageGroupSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(sender=request.user, father_group=group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
