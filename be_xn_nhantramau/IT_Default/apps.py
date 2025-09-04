from django.apps import AppConfig


class ITDefaultConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "IT_Default"

    def ready(self):
        import IT_Default.signals  # This line connects the signals
