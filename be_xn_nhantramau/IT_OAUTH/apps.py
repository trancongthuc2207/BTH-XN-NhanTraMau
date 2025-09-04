from django.apps import AppConfig


class ITOAUTHConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "IT_OAUTH"

    def ready(self):
        import IT_OAUTH.signals  # This line connects the signals

        # import IT_OAUTH.core.signals  # type: ignore
