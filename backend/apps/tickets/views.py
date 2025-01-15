from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from urllib3 import request

from backend.apps.tickets.serializers import CreateTicketSerializer, TicketSerializer, TicketMessageSerializer
from backend.apps.tickets.permissions import IsEmployee, IsBusiness, IsMemberOfChat
from backend.apps.tickets.models import Ticket, TicketChat, TicketMessage

from backend.apps.customuser.models import CustomUser
from backend.apps.space.models import Space

class CreateTicketView(generics.CreateAPIView):
    permission_classes = (IsBusiness,)

    def post(self, request, *args, **kwargs):
        serializer = CreateTicketSerializer(data=request.data, context={"request":request})
        
        if serializer.is_valid():
            serializer.save(serializer.data)
            return Response({"message":"Ticket successfully created"}, status=status.HTTP_201_CREATED)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        

class GetWaitingTickets(generics.ListAPIView):
    queryset = Ticket.objects.filter(status="waiting")
    permission_classes = (IsEmployee,)
    serializer_class = TicketSerializer

class GetClosedTickets(generics.ListAPIView):
    queryset = Ticket.objects.filter(status="closed")
    permission_classes = (IsEmployee,)
    serializer_class = TicketSerializer


class TookTicket(APIView):
    permission_classes = (IsEmployee,)
    
    def get(self, request, ticket_pk, *args, **kwargs):
        try:
            employee = request.user
            ticket = Ticket.objects.get(pk=ticket_pk)

            # check if the ticket already has an employee
            if ticket.employee:
                return Response({"error":"Another employee took this ticket already."}, status=status.HTTP_400_BAD_REQUEST)
            
            if ticket.status != "waiting":
                return Response({"error":f"You can't take the ticket with id {ticket_pk} because it already taken or closed"}, status=status.HTTP_400_BAD_REQUEST)
            
            ticket.employee = employee
            #adding the employee to space 
            if ticket.help_in_space:
                space = Space.objects.get(id=ticket.space_pk)
                space.members.add(employee)
            
            # creating chat
            chat = TicketChat.objects.create(
                user=ticket.user,
                employee=employee,
            )
            ticket.status = "in_process"
            ticket.chat_id = chat.id
            
            ticket.save()
            return Response({"message":f"Ticket with id: {ticket_pk} has been attached to employee with id: {employee.id} successfully!"}, status=status.HTTP_200_OK)                
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CloseTicket(APIView):
    permission_classes = (IsEmployee,)
    def get(self, request, ticket_pk, *args, **kwargs):
        try:
            employee = request.user
            ticket = Ticket.objects.get(pk=ticket_pk)

            if ticket.status != 'in_process':
                return Response({"error":f"You can't close the ticket with id {ticket_pk} because it isn't started or already closed or not started"}, status=status.HTTP_400_BAD_REQUEST)
            if ticket.employee != employee:
                return Response({"error":f"The employee with id {employee.id} are not the one that took the ticket with id {ticket.id}"}, status=status.HTTP_400_BAD_REQUEST)

            # closing ticket and deleting chat
            if ticket.space_pk and ticket.help_in_space:
                space = Space.objects.get(id=ticket.space_pk) 
                space.members.remove(employee)    
                                            
            # deliting ticket chat
            chat = ticket.chat
            if chat:
                ticket.chat = None
                chat.delete()
            

            ticket.status = "closed"

            ticket.save() 
            return Response({"message":f"The ticket with {ticket.id} has been successfully closed by employee with id {employee.id}"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TicketChatView(APIView):
    permission_classes = (IsMemberOfChat, IsAuthenticated)

    def get(self, request, chat_id):
        """Get all unsee messanges"""
        chat = TicketChat.objects.get(id=chat_id)
        messages = TicketMessage.objects.filter(father_chat=chat, seen=False)
        response = [
            {
                "sender": message.sender.username,
                "email": message.sender.email,
                "text": message.text,
                "created_at": message.created_at.strftime("%H:%M")
            }
            for message in messages
        ]

        for message in messages:
            message.seen = True
            message.save()

        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, chat_id, *args, **kwargs):
        """Send message"""
        try:
            chat = TicketChat.objects.get(id=chat_id)
            ticket = Ticket.objects.get(chat=chat)
            sender = request.user

            if sender.id == ticket.user:
                reciver = ticket.employee
            else:
                reciver = ticket.user

            serializer = TicketMessageSerializer(data=request.data)
            if serializer.is_valid():
                TicketMessage.objects.create(
                    sender=sender,
                    father_chat=chat,
                    text=request.data.get("text"),
                )

                return Response({"message":f"Your message is send to user with id {reciver.id}"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetMyTickets(generics.GenericAPIView):
    serializer_class = TicketSerializer

    def get(self, request, *args, **kwargs):
        queryset1 = Ticket.objects.filter(user=request.user)
        queryset2 = Ticket.objects.filter(employee=request.user)
        queryset = queryset1 | queryset2
        serializer = TicketSerializer(queryset, many=True)
        return Response(serializer.data)
