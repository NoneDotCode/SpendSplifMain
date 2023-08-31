from django.apps import AppConfig


class TotalBalanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.total_balance'

    def ready(self):
        from apps.total_balance.signals import update_total_balance
