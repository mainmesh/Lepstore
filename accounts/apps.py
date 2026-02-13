from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Import signals or models to ensure UserProfile is created
        try:
            import accounts.models  # noqa: F401
        except Exception:
            pass
