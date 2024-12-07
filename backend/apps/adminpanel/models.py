from django.db import models
# ПЕРЕНЕСТИ В app adminpanel

class ProjectOverview(models.Model):
    space_id = models.IntegerField()
    assets = models.CharField(max_length=50, verbose_name="Тип активу")
    data = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Дані")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Ціна")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    def str(self):
        return f"{self.space_id} - {self.assets}"