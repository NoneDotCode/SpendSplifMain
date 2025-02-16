from django.urls import path
from backend.apps.tickets.views import CreateTicketView, GetWaitingTickets, GetClosedTickets, \
    TookTicket, CloseTicket, TicketChatView, GetMyTickets

urlpatterns = [
    path("tickets/create/", CreateTicketView.as_view(), name="create_ticket"),
    path("tickets/waiting/", GetWaitingTickets.as_view(), name="get_waiting_tickets"),
    path("tickets/closed/", GetClosedTickets.as_view(), name="get_closed_tickets"),
    path("tickets/took/<int:ticket_pk>/", TookTicket.as_view(), name="took_ticket"),
    path("tickets/close/<int:ticket_pk>/", CloseTicket.as_view(), name="close_ticket"),
    path('tickets/<int:chat_id>/', TicketChatView.as_view(), name='ticket_chat'),
    path('tickets/my_tickets/', GetMyTickets.as_view(), name='my_tickets'),
]
