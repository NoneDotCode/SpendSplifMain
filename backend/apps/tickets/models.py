from datetime import datetime

from django.db import models

from backend.apps.customuser.models import CustomUser

class TicketChat(models.Model):
        user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="ticket_user")
        employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="ticket_employee")
        user_last_visit = models.DateTimeField(blank=True, default= datetime(2024, 1, 1, 12)) # literally none
        employee_last_visit = models.DateTimeField(blank=True, default= datetime(2024, 1, 1, 12))

        def str(self):
            return f"Chat between {self.user.username} and {self.employee.username}"

class TicketMessage(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sender")
    text = models.CharField(max_length=800)
    seen = models.BooleanField(default=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    father_chat = models.ForeignKey(TicketChat, on_delete=models.CASCADE)

    def __str__(self):
        return self.text
    
class Ticket(models.Model):
    TICKET_STATUS_CHOICES = (
        ("waiting","waiting"),
        ("in_process", "in_process"),
        ("closed", "closed"),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_that_needs_help")
    help_in_space = models.BooleanField(default=False, blank=True)
    space_pk = models.IntegerField(blank=True, null=True) #optional
    title = models.TextField(max_length=40, blank=True, null=True)
    message = models.TextField(max_length=800)
    status = models.CharField(max_length=10, choices=TICKET_STATUS_CHOICES, default="waiting")
    chat = models.ForeignKey(TicketChat, on_delete=models.CASCADE, blank=True, null=True)
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True) #optional
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.id} - {self.message}"
    