from django.apps import AppConfig
import os

class CommandsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'CommandsCustom'
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'CommandsCustom')
