from typing import Dict, Any

import requests

#
#
# class Currency_convertor:
#     # empty dict to store the conversion rates
#     rates = {}
#
#     def __init__(self, url):
#         data = requests.get(url).json()
#
#         # Extracting only the rates from the json data
#         self.rates = data["rates"]
#
#     # function to do a simple cross multiplication between
#     # the amount and the conversion rates
#     def convert(self, from_currency, to_currency, amount):
#         initial_amount = amount
#         if from_currency != 'EUR':
#             amount = amount / self.rates[from_currency]
#
#         # limiting the precision to 2 decimal places
#         amount = round(amount * self.rates[to_currency], 2)
#         print('{} {} = {} {}'.format(initial_amount, from_currency, amount, to_currency))
#
#
# # Driver code
# if __name__ == "__main__":
#     # YOUR_ACCESS_KEY = 'GET YOUR ACCESS KEY FROM fixer.io'
#     url = str.__add__('http://data.fixer.io/api/latest?access_key=', "65268712d3852ba0ad7d085115ac7118")
#     c = Currency_convertor(url)
#     from_country = input("From Country: ")
#     to_country = input("TO Country: ")
#     amount = int(input("Amount: "))
#
#     c.convert(from_country, to_country, amount)
#
#

url = str.__add__('http://data.fixer.io/api/latest?access_key=', "65268712d3852ba0ad7d085115ac7118")
data = requests.get(url).json()
rates = data["rates"]

result = []

with open("P:\My_Projects\SpendSpl\\apps\converter\currencies.txt", "r") as file:
    for i in file.readlines()[2:]:
        for j in [(i[2:-13].strip() + " - " + i[36:].strip()[:-1].strip()).split(' - ')]:
            result.append(j + [rates[j[1]]])

print(*sorted(result, key=lambda x: x[0]), sep='\n')

print(rates)