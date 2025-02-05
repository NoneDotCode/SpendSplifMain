# from rest_framework import serializers, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.conf import settings
# from django.shortcuts import get_object_or_404
# from django.utils import timezone
# from datetime import timedelta
# from rest_framework.request import Request

# from backend.apps.customuser.models import CustomUser
# from backend.apps.space.models import Space, MemberPermissions
# from backend.apps.cards.models import UserSpace, ClientToken
# from .serializers import FinAPICreateTokenSerializer, UserCreateSerializer, FinAPIRefreshTokenSerializer

# import string
# import random
# import uuid
# import requests


# def generate_secure_password(length=12):
#     """Генерирует случайный безопасный пароль"""
#     characters = string.ascii_letters + string.digits + string.punctuation
#     return ''.join(random.choice(characters) for _ in range(length))

# def get_finapi_token():
#         """Get the latest FinAPI token from database"""
#         try:
#             token_obj = ClientToken.objects.first()
#             if token_obj and token_obj.access_token:
#                 return token_obj.access_token
#             return None
#         except ClientToken.DoesNotExist:
#             return None

# class UserAuthView(APIView):
#     permission_classes = [IsAuthenticated]    

#     def post(self, request, space_pk):
#         serializer = UserCreateSerializer(
#             data=request.data,
#             context={'space_pk': space_pk}
#         )

#         space = Space.objects.filter(pk=space_pk).first()

#         if UserSpace.objects.filter(space=space).exists():
#             user_space = UserSpace.objects.get(space=space)
#             # Проверяем, прошло ли более часа с момента последнего обновления
#             if user_space.updated_at > timezone.now() - timedelta(hours=1):
#                 # Если прошло меньше часа, возвращаем текущие токены
#                 return {
#                     'access_token': user_space.access_token,
#                     'refresh_token': user_space.refresh_token
#                 }
#             else:
#                 get_tokens = self.refresh_finapi_tokens(space=space)
#                 return get_tokens
        
#         if serializer.is_valid():
#             space = serializer.validated_data['space']
#             member_email = serializer.validated_data['member_email']
#             generated_password = generate_secure_password()
            
#             # Генерируем уникальный ID для пользователя
#             user_id = f"{space.id},{space.title}"
            
#             # Создание пользователя через FinAPI
#             finapi_user_response = self.create_finapi_user(
#                 user_id=user_id,
#                 email=member_email,
#                 password=generated_password,
#                 phone=serializer.validated_data['phone']
#             )
            
#             if finapi_user_response.status_code != 201:
#                 return finapi_user_response
            
#             # Получаем данные о созданном пользователе
#             finapi_user_data = finapi_user_response.json()
            
#             # Создаем токены для пользователя
#             tokens_response = self.create_finapi_tokens(
#                 username=user_id, 
#                 password=generated_password, 
#                 space=space, 
#                 phone=serializer.validated_data['phone']
#             )
            
#             if tokens_response.status_code != 200:
#                 return tokens_response
            
#             # Токены успешно получены
#             tokens_data = tokens_response.data
            
#             return Response(tokens_data, status=status.HTTP_201_CREATED)
        
#         return Response(
#             serializer.errors,
#             status=status.HTTP_422_UNPROCESSABLE_ENTITY
#         )
    
#     def create_finapi_user(self, user_id, email, password, phone):
#         """
#         Создание пользователя через FinAPI
#         """
#         token = get_finapi_token()
#         if not token:
#             return Response(
#                 {'error': 'No valid token found'}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         headers = {
#             'Authorization': f'Bearer {token}',
#             'Content-Type': 'application/json',
#             'X-Request-Id': str(uuid.uuid4())
#         }
        
#         payload = {
#             'id': user_id,
#             'email': email,
#             'password': password,
#             'phone': phone,
#             'isAutoUpdateEnabled': False
#         }
        
#         try:
#             response = requests.post(
#                 'https://sandbox.finapi.io/api/v2/users',
#                 json=payload,
#                 headers=headers
#             )
#             return response
        
#         except requests.exceptions.RequestException as e:
#             return Response(
#                 {'error': str(e)}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )
    
#     def create_finapi_tokens(self, username, password, space, phone):
#         """
#         Создание токенов и запись в UserSpace
#         """
#         token_serializer = FinAPICreateTokenSerializer(data={
#             'grant_type': "password",
#             'client_id': settings.FINAPI_CLIENT_ID,
#             'client_secret': settings.FINAPI_CLIENT_SECRET,
#             'username': username,
#             'password': password,
#         })
        
#         if token_serializer.is_valid():
#             try:
#                 response_data = token_serializer.save()
                
#                 # Создаем запись в UserSpace
#                 UserSpace.objects.create(
#                     username=username,
#                     space=space,
#                     password=password,
#                     refresh_token=response_data.get('refresh_token', ''),
#                     phone=phone
#                 )
                
#                 return Response(response_data, status=status.HTTP_200_OK)
            
#             except Exception as e:
#                 return Response(
#                     {'error': str(e)}, 
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#         return Response(
#             token_serializer.errors, 
#             status=status.HTTP_400_BAD_REQUEST
#         )
        
#     def refresh_finapi_tokens(self, space):
#         """
#         Refresh FinAPI tokens for a given space
#         """
#         try:
#             userSpace = UserSpace.objects.get(space=space)
#         except UserSpace.DoesNotExist:
#             return Response(
#                 {'error': 'User space not found'}, 
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         token_serializer = FinAPIRefreshTokenSerializer(data={
#             'grant_type': 'refresh_token',
#             'client_id': settings.FINAPI_CLIENT_ID,
#             'client_secret': settings.FINAPI_CLIENT_SECRET,
#             'refresh_token': userSpace.refresh_token,
#         })
        
#         try:
#             token_data = token_serializer.save()
#             return Response(token_data, status=status.HTTP_200_OK)
        
#         except serializers.ValidationError as e:
#             return Response(
#                 {'error': str(e)}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        

# class BankConnectionImportView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, space_pk):
#         space = Space.objects.filter(pk=space_pk).first()
#         if not space:
#             return Response({'error': 'Space not found'}, status=status.HTTP_404_NOT_FOUND)

#         phone = request.data.get('phone')
#         if not phone:
#             return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
        
#         # Проверка на корректность номера телефона (например, в формате +420123456789 для Чехии)
#         phone_regex = r'^\+420\d{9}$'
#         if not re.match(phone_regex, phone):
#             return Response({'error': 'Invalid phone number format'}, status=status.HTTP_400_BAD_REQUEST)

#         bank_connection_name = request.data.get('bankConnectionName')
#         if bank_connection_name:
#             if len(bank_connection_name) < 1 or len(bank_connection_name) > 64:
#                 return Response({'error': 'Bank connection name must be between 1 and 64 characters'}, 
#                                  status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response({'error': 'Bank connection name is required'}, status=status.HTTP_400_BAD_REQUEST)

#         # Создаём экземпляр UserAuthView и вызываем его метод post
#         user_auth_view = UserAuthView()
#         auth_request = Request(
#             request=request._request,
#             data={'space': space, 'phone': phone}
#         )
#         auth_response = user_auth_view.post(auth_request, space_pk)

#         if auth_response.status_code != status.HTTP_201_CREATED:
#             return auth_response

#         tokens_data = auth_response.data.get('access_token')
#         if not tokens_data:
#             return Response({'error': 'Failed to retrieve user token'}, status=status.HTTP_400_BAD_REQUEST)

#         payload = {
#             "bank": {"search": "IBAN"},
#             "bankConnectionName": request.data.get("bankConnectionName", None),
#             "maxDaysForDownload": 60,
#             "allowedInterfaces": ["XS2A"],
#             "redirectUrl": "https://spendsplif.com/",
#             "allowTestBank": True
#         }

#         headers = {
#             'Authorization': f'Bearer {tokens_data}',
#             'Content-Type': 'application/json',
#             'X-Request-Id': str(uuid.uuid4())
#         }

#         try:
#             response = requests.post(
#                 'https://sandbox.finapi.io/api/v2/webForms/bankConnectionImport',
#                 json=payload,
#                 headers=headers
#             )
#             return Response(response.json(), status=response.status_code)
#         except requests.RequestException as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
