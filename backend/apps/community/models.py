from django.db import models

from backend.apps.customuser.models import CustomUser

class Post(models.Model):
    country_choices = [
        ("germany","Germany"),
        ("czechia","Czechia"),
        ("usa","USA"),
        ("ukraine","Ukraine"),
    ]
    
    title = models.CharField(max_length=100)
    text = models.TextField()
    country = models.CharField(max_length=10,choices=country_choices)
    date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(CustomUser)
    views_counter = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.title} - {self.views_counter}"
