import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from IT_OAUTH.models import User


class Command(BaseCommand):
    help = "Initialize default roles and users from a JSON file"

    def handle(self, *args, **kwargs):
        path = os.path.join(settings.BASE_DIR, 'IT_OAUTH',
                            'fixtures', 'init_user_roles.json')

        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f"JSON file not found: {path}"))
            return

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Insert users
        for user_data in data.get("users", []):
            user = User.objects.filter(username=user_data["username"]).first()
            if not user:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    is_staff=True,
                    is_superuser=user_data["is_superuser"]
                )
                user.set_password("123456")
                user.save()
