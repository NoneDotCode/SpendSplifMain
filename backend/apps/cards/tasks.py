# import requests
# from django.conf import settings
# from celery import shared_task
#
# from backend.apps.cards.models import ClientToken
#
# @shared_task
# def update_finapi_tokens():
#     """Update FinAPI tokens every hour"""
#     url = "https://sandbox.finapi.io/api/v2/oauth/token"
#
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }
#
#     data = {
#         'grant_type': "client_credentials",
#         'client_id': settings.FINAPI_CLIENT_ID,
#         'client_secret': settings.FINAPI_CLIENT_SECRET,
#     }
#
#     try:
#         response = requests.post(url, headers=headers, data=data)
#         response.raise_for_status()
#
#         token_data = response.json()
#
#         # Get or create token object
#         token_obj, created = ClientToken.objects.get_or_create(pk=1)
#
#         # Update token data
#         token_obj.access_token = token_data.get('access_token')
#         token_obj.refresh_token = token_data.get('refresh_token')
#         token_obj.save()
#
#         return "Tokens updated successfully"
#
#     except requests.RequestException as e:
#         return f"Error updating tokens: {str(e)}"