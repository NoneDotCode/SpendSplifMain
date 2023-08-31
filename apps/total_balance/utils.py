from rest_framework.reverse import reverse

import requests


def convert_currency(from_currency, to_currency, amount):
    url = str.__add__('http://127.0.0.1:8000', reverse('converter'))
    print(url)
    data = {'from_currency': from_currency, 'to_currency': to_currency, 'amount': amount}
    headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNj'
                                'kzMjM5NjYxLCJpYXQiOjE2OTMyMzc2NzYsImp0aSI6IjAyNzkxOTUyNDMyNzQxYTg4YjA3MDQ1ZjJhYTNmYmU2'
                                'IiwidXNlcl9pZCI6MX0.xPCfTFC4CAU12ExE_vuGHg3sgaOysjHzE1w90VEEGQI'}
    response = requests.get(url, headers=headers, json=data)
    return response.json()['converted_amount']