from django.db import models

from backend.apps.space.models import Space

from django.core.validators import MaxValueValidator

class Goal(models.Model):
    title = models.CharField(max_length=40)
    goal = models.DecimalField(max_digits=12, decimal_places=2,validators=[MaxValueValidator(99000000000)])
    collected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    father_space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def collected_percentage(self):
        if self.goal:
            return (self.collected / self.goal) * 100
        return 0
