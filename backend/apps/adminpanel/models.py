from django.db import models

class ProjectOverview(models.Model):
    space_id = models.IntegerField()
    assets = models.CharField(max_length=50, )
    data = models.DecimalField(max_digits=12, decimal_places=3)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    updated_date = models.DateField(auto_now=False)

    def str(self):
        return f"{self.space_id} - {self.assets}"
