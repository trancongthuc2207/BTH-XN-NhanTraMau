from django.apps import AppConfig
import os

class GeneralUtilsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'general_utils'
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'general_utils')
