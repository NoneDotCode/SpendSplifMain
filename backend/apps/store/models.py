from django.db import models

class PaymentHistory(models.Model):
    space_id = models.IntegerField()
    payment_category  = models.CharField(max_length=50,) # the value can only be subscription/service/license
    amount = models.DecimalField(max_digits=12, decimal_places=2,)
    date = models.DateTimeField(auto_now=True,)

    def str(self):
        return f"{self.space_id} - {self.assets}"