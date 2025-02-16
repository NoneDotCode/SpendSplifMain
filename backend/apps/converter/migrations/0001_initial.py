# backend/apps/converter/migrations/0001_initial.py

from django.db import migrations, models
import requests
import environ
import os
from backend.apps.converter.constants import CURRENCIES

env = environ.Env()
BASE_DIR = os.path.dirname(os.path.abspath("../../config/.."))
environ.Env.read_env(os.path.join(BASE_DIR, "dev.env"))

def fill_currencies(apps, schema_editor):
    Currency = apps.get_model('converter', 'Currency')
    try:
        url = str.__add__('http://data.fixer.io/api/latest?access_key=', env("FIXER_API_TOKEN"))
        print(f"Fetching data from: {url}")
        
        response = requests.get(url)
        data = response.json()
        print(f"Received data: {data}")
        
        rates = data["rates"]
        result = []

        for i in CURRENCIES:
            result.append(i + [rates[i[1]], ])
            print(f"Processing currency: {i}")

        for i in sorted(result, key=lambda x: x[0]):
            Currency.objects.create(
                currency=i[0],
                iso_code=i[1],
                euro=i[2]
            )
            print(f"Created currency: {i[0]}")
    except Exception as e:
        print(f"Error in fill_currencies: {e}")

def reverse_currencies(apps, schema_editor):
    Currency = apps.get_model('converter', 'Currency')
    Currency.objects.all().delete()

class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(max_length=30)),
                ('iso_code', models.CharField(max_length=3)),
                ('euro', models.DecimalField(decimal_places=2, max_digits=10)),
                ('time_update', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RunPython(fill_currencies, reverse_currencies),
    ]