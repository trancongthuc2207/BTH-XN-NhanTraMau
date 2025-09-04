from django.apps import AppConfig


class IT_MailManagerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "IT_MailManager"

    def ready(self):
        import IT_MailManager.signals  # This line connects the signals
