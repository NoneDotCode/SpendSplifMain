from django.urls import path

from backend.apps.spend.views import SpendView

from backend.apps.spend.views import (PeriodicSpendCreateView, PeriodicSpendDeleteView, PeriodicSpendEditView,
                                      PeriodicSpendsGetView)

urlpatterns = [
    path("spend/", SpendView.as_view(), name="spend"),
    path("create_periodic_spend/", PeriodicSpendCreateView.as_view(), name="periodic_spend_create"),
    path("delete_periodic_spend/<int:pk>/", PeriodicSpendDeleteView.as_view(),
         name="periodic_spend_delete"),
    path("periodic_spends/<int:pk>/", PeriodicSpendEditView.as_view(), name="periodic_spend_edit"),
    path("periodic_spends/", PeriodicSpendsGetView.as_view(), name="check_periodic_spends")
]
