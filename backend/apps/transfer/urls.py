from django.urls import path

from backend.apps.transfer.views import TransferAccToAccView, TransferAccToGoalView, TransferGoalToAccView

urlpatterns = [
    path("transfer/acc_to_acc", TransferAccToAccView.as_view(), name="transfer_acc_to_acc"),
    path("transfer/acc_to_goal", TransferAccToGoalView.as_view(), name="transfer_acc_to_goal"),
    path("transfer/goal_to_acc", TransferGoalToAccView.as_view(), name="transfer_goal_to_acc"),
]
