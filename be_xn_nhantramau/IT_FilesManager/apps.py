from django.apps import AppConfig


class IT_FilesManagerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "IT_FilesManager"

    def ready(self):
        import IT_FilesManager.signals  # This line connects the signals
