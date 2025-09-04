import os
from django.apps import AppConfig, apps
from django.conf import settings


class S_SystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "S_SystemConfig"
    path = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), "S_SystemConfig")

    installed_app_names = []

    def ready(self):
        # ... (existing logic to populate installed_app_names from apps.get_app_configs()) ...
        # This part remains the same, as it reads the final INSTALLED_APPS list.
        if not settings.DEBUG:
            pass

        S_SystemConfig.installed_app_names = []

        for app_config in apps.get_app_configs():
            app_display_name = getattr(
                app_config, 'verbose_name', app_config.name)
            S_SystemConfig.installed_app_names.append(app_display_name)

        print("\n--- Installed Apps Detected by S_SystemConfig ---")
        for app_name in S_SystemConfig.installed_app_names:
            print(f"- {app_name}")
        print("---------------------------------------------\n")
