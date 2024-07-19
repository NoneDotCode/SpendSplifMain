from django.db import models


class Cryptocurrency(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20)
    price_usd = models.DecimalField(max_digits=15, decimal_places=2)
    price_eur = models.DecimalField(max_digits=15, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.symbol}): {self.price_usd} USD, {self.price_eur} EUR"
