from django.http import JsonResponse
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from backend.apps.customuser.models import CustomUser
from backend.apps.messenger.models import DmMessage, DmChat, SpaceGroup, MessageGroup, MessengerSettings
from backend.apps.messenger.permissions import IsMemberOfDmChat
from backend.apps.messenger.serializers import DmMessageSerializer, MessageGroupSerializer, MessengerSettingsSerializer
from rest_framework.response import Response
from rest_framework import status
from backend.apps.space.models import Space


class CreateChatView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsMemberOfDmChat, IsAuthenticated]

    @staticmethod
    def get(request, owner_1_id, owner_2_id):
        chat = DmChat.objects.filter(owner_1_id=owner_1_id, owner_2_id=owner_2_id).first()
        if not chat:
            return JsonResponse({'error': 'Chat not found'}, status=404)
        messages = DmMessage.objects.filter(father_chat=chat)
        response = {
            'messages': [{'sender': message.sender.username, 'text': message.text} for message in messages]
        }
        return JsonResponse(response)

    @staticmethod
    def post(request, owner_1_id, owner_2_id):
        chat = DmChat.objects.filter(owner_1_id=owner_1_id, owner_2_id=owner_2_id).first()
        sender = request.user
        receiver = CustomUser.objects.get(id=owner_2_id)

        receiver_messenger_settings = MessengerSettings.objects.get_or_create(user=receiver)[0]
        if receiver_messenger_settings.can_text == 'nobody':
            return JsonResponse({'error': 'Sending messages is not allowed for this user'}, status=403)
        elif receiver_messenger_settings.can_text == 'people_in_space':
            if not Space.objects.filter(members=sender).filter(members=receiver).exists():
                return JsonResponse({'error': 'User is not a member of any space'}, status=403)

        serializer = DmMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=sender, father_chat_id=chat.id)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SpaceChatView(generics.GenericAPIView):

    @staticmethod
    def get(request, group_id):
        group = get_object_or_404(SpaceGroup, id=group_id)
        messages = MessageGroup.objects.filter(father_group=group)
        serializer = MessageGroupSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def post(request, group_id):
        group = get_object_or_404(SpaceGroup, id=group_id)
        if request.user not in group.father_space.members.all():
            return Response("User not found in the space", status=status.HTTP_400_BAD_REQUEST)

        request.data['father_group'] = group.id
        serializer = MessageGroupSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(sender=request.user, father_group=group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessengerSetSettingsWhoCanText(generics.GenericAPIView):
    @staticmethod
    def get(request, **kwargs):
        user = request.user
        messenger_settings, created = MessengerSettings.objects.get_or_create(user=user)
        serializer = MessengerSettingsSerializer(messenger_settings)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def put(request, **kwargs):
        user = request.user
        
        messenger_settings, created = MessengerSettings.objects.get_or_create(user=user)
        
        if request.data.get("can_text") == "nobody":
            messenger_settings.can_text = 'nobody'
        elif request.data.get("can_text") == 'people_in_space':
            messenger_settings.can_text = 'people_in_space'
        elif request.data.get("can_text") == 'everybody':
            messenger_settings.can_text = 'everybody'
        else:
            return Response({"message": "Invalid settings value"}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.data.get("notification") is True:
            messenger_settings.notification_enabled = True
        elif request.data.get("notification") is False:
            messenger_settings.notification_enabled = False
        else:
            return Response({"message": "Invalid notification value"}, status=status.HTTP_400_BAD_REQUEST)
        
        messenger_settings.save()

        serializer = MessengerSettingsSerializer(messenger_settings)
        return Response(serializer.data, status=status.HTTP_200_OK)
