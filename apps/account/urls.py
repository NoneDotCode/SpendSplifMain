from django.urls import path

from apps.account.views import ViewAccount, EditAccount, CreateAccount, DeleteAccount, IncomeView

urlpatterns = [
    path("create_account/", CreateAccount.as_view(), name="create_account"),
    path("space_accounts/", ViewAccount.as_view(), name="all_space_accounts"),
    path("space_accounts/<int:pk>/", EditAccount.as_view(), name="edit_account"),
    path("delete_account/<int:pk>/", DeleteAccount.as_view(), name="delete_account"),
    path("space_accounts/<int:pk>/income/", IncomeView.as_view(), name="income_to_account")
]
