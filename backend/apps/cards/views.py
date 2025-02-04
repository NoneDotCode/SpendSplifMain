# from rest_framework import serializers, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.conf import settings
# from django.shortcuts import get_object_or_404

# from backend.apps.customuser.models import CustomUser
# from backend.apps.space.models import Space, MemberPermissions, UserSpace
# from .serializers import FinAPITokenSerializer, UserCreateSerializer

# import string
# import random
# import uuid
# import requests

# def generate_secure_password(length=12):
#     """Генерирует случайный безопасный пароль"""
#     characters = string.ascii_letters + string.digits + string.punctuation
#     return ''.join(random.choice(characters) for _ in range(length))

# class UserCreateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, space_pk):
#         serializer = UserCreateSerializer(
#             data=request.data,
#             context={'space_pk': space_pk}
#         )
        
#         if serializer.is_valid():
#             user = request.user
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
            
#             return Response(tokens_data, finapi_user_data, status=status.HTTP_201_CREATED)
            
#         return Response(
#             serializer.errors,
#             status=status.HTTP_422_UNPROCESSABLE_ENTITY
#         )
    
#     def create_finapi_user(self, user_id, email, password, phone):
#         """
#         Создание пользователя через FinAPI
#         """
#         headers = {
#             'Authorization': f'Bearer {settings.FINAPI_CLIENT_ACCESS_TOKEN}',
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
#         token_serializer = FinAPITokenSerializer(data={
#             'grant_type': "password",
#             'client_id': settings.FINAPI_CLIENT_ID,
#             'client_secret': settings.FINAPI_CLIENT_SECRET,
#             'username': username,
#             'password': password,
#         })
        
#         if token_serializer.is_valid():
#             try:
#                 token_data = token_serializer.save()
                
#                 # Создаем запись в UserSpace
#                 UserSpace.objects.create(
#                     space=space,
#                     password=password,
#                     refresh_token=token_data.get('refresh_token', ''),
#                     phone=phone
#                 )
                
#                 return Response(token_data, status=status.HTTP_200_OK)
            
#             except Exception as e:
#                 return Response(
#                     {'error': str(e)}, 
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
        
#         return Response(
#             token_serializer.errors, 
#             status=status.HTTP_400_BAD_REQUEST
#         )