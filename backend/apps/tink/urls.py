from django.urls import path

from backend.apps.tink.views import (AuthorizeAppView, CreateUserView, GenerateAuthorizationCodeView,
                                     GrantUserAccessView, BuildTinkURLView, GetAuthorizationCodeView,
                                     GetUserAccessTokenView, ListTransactionsView, AddAccountsView,
                                     ListTinkAccountsView, FullIntegrationView)

urlpatterns = [
    path("authorize/", AuthorizeAppView.as_view(), name="tink_authorize"),
    path("create_user/", CreateUserView.as_view(), name="tink_create_user"),
    path("generate_auth_code/", GenerateAuthorizationCodeView.as_view(), name="generate_auth_code"),
    path("grant_user_access/", GrantUserAccessView.as_view(), name="grant_user_access"),
    path('build_tink_url/', BuildTinkURLView.as_view(), name='build-tink-url'),
    path('get_authorization_code/', GetAuthorizationCodeView.as_view(), name='get_authorization_code'),
    path('get_user_access_token/', GetUserAccessTokenView.as_view(), name='get_user_access_token'),
    path('list_transactions/', ListTransactionsView.as_view(), name='list_transactions'),
    path('my_spaces/<int:space_pk>/add_accounts/', AddAccountsView.as_view(), name='add_accounts'),
    path('my_spaces/<int:space_pk>/list_accounts/', ListTinkAccountsView.as_view(), name='list_accounts'),
    path('my_spaces/<int:space_pk>/full_integration/', FullIntegrationView.as_view(), name='full_integration_tink')
]
