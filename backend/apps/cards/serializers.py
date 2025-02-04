# from rest_framework import serializers
# from django.conf import settings
# from backend.apps.space.models import Space
# from backend.apps.space.models import MemberPermissions
# import requests
# from django.shortcuts import get_object_or_404

# class FinAPITokenSerializer(serializers.Serializer):
#     """
#     Serializer for handling FinAPI OAuth token requests
#     """
#     grant_type = serializers.ChoiceField(
#         choices=['password', 'client_credentials', 'refresh_token']
#     )
#     client_id = serializers.CharField(required=True)
#     client_secret = serializers.CharField(required=True)
#     username = serializers.CharField(required=False, allow_null=True)
#     password = serializers.CharField(required=False, allow_null=True)
#     refresh_token = serializers.CharField(required=False, allow_null=True)

#     def validate(self, attrs):
#         """
#         Validate request parameters based on grant type
#         """
#         grant_type = attrs.get('grant_type')
        
#         if grant_type == 'password':
#             if not attrs.get('username') or not attrs.get('password'):
#                 raise serializers.ValidationError("Username and password are required for password grant type")
        
#         elif grant_type == 'refresh_token':
#             if not attrs.get('refresh_token'):
#                 raise serializers.ValidationError("Refresh token is required for refresh_token grant type")
        
#         return attrs

#     def create(self, validated_data):
#         """
#         Send token request to FinAPI and handle response
#         """
#         try:
#             response = requests.post(
#                 'https://sandbox.finapi.io/oauth/token',
#                 data={
#                     'grant_type': validated_data['grant_type'],
#                     'client_id': validated_data['client_id'],
#                     'client_secret': validated_data['client_secret'],
#                     'username': validated_data.get('username', ''),
#                     'password': validated_data.get('password', ''),
#                 },
#                 headers={
#                     'Content-Type': 'application/x-www-form-urlencoded',
#                 }
#             )
#             response.raise_for_status()
#             return response.json()
#         except requests.exceptions.RequestException as e:
#             raise serializers.ValidationError(f"Token request failed: {str(e)}")


# class UserCreateSerializer(serializers.Serializer):
#     phone = serializers.CharField(max_length=20)

#     def validate(self, data):
#         space_pk = self.context.get('space_pk')
#         if not space_pk:
#             raise serializers.ValidationError("space_pk is required")

#         # Получаем Space по ID
#         space = get_object_or_404(Space, pk=space_pk)
        
#         # Ищем пользователя с нужной ролью среди members
#         member = MemberPermissions.objects.filter(
#             space=space,
#             member__roles__contains=['business_plan']
#         ).first()

#         if not member:
#             member = MemberPermissions.objects.filter(
#                 space=space,
#                 member__roles__contains=['business_lic']
#             ).first()

#         if not member:
#             raise serializers.ValidationError(
#                 "Space must have a member with business_plan or business_lic role"
#             )

#         data.update({
#             'space': space,
#             'member_email': member.member.email
#         })
#         return data