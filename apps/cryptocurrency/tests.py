# from django.test import TestCase
# from .models import Cryptocurrency
# from .tasks import update_cryptocurrency_rates
# from unittest.mock import patch
#
# class CryptocurrencyTests(TestCase):
#
#     @patch('requests.get')
#     def test_update_cryptocurrency_rates(self, mock_get):
#         # Подмена ответа от API
#         mock_get.return_value.json.return_value = {
#             'bitcoin': {'usd': 50000, 'eur': 42000},
#             'ethereum': {'usd': 4000, 'eur': 3500}
#         }
#
#         # Вызов функции обновления курсов
#         update_cryptocurrency_rates()
#
#         # Проверка, что записи созданы в базе данных
#         self.assertEqual(Cryptocurrency.objects.count(), 2)
#         bitcoin = Cryptocurrency.objects.get(symbol='bitcoin')
#         self.assertEqual(bitcoin.price_usd, 50000)
#         self.assertEqual(bitcoin.price_eur, 42000)