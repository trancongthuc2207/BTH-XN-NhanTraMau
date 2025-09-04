from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.apps import apps
from .models import *


@receiver(post_migrate)
def sync_new_app(sender, **kwargs):
    try:
        if sender.name == 'IT_MailManager':
            # Sync or create necessary models or perform initial setup
            LogEntryApp.objects.using('default').get_or_create(
                user=None, action_flag=ADDITION, change_message="Initial setup for IT_MailManager"
            )
            print("IT_MailManager app has been initialized.")

    except Exception as e:
        print(e)
