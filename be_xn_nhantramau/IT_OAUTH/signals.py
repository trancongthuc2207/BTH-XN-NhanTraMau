# accounts/signals.py
import json
import os
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
from django.db.utils import IntegrityError
from django.conf import settings
from IT_OAUTH.models import ConfigApp

# Tên file JSON của bạn
INIT_USER_JSON = "init_user.json"
INIT_CONFIG_JSON = "init_config.json"


@receiver(post_migrate)
def load_initial_users_and_configs_signal(sender, **kwargs):
    """
    Tải dữ liệu người dùng và cấu hình ban đầu từ các file JSON.
    """
    # Chỉ chạy signal này cho app 'IT_OAUTH'
    if not sender.name == "IT_OAUTH":
        return

    # === SECTION 1: Tải dữ liệu Người Dùng ===
    User = apps.get_model("IT_OAUTH", "User")
    Role = apps.get_model("IT_OAUTH", "Role")

    fixture_dir = os.path.join(sender.path, "fixtures")
    user_fixture_path = os.path.join(fixture_dir, INIT_USER_JSON)

    if os.path.exists(user_fixture_path):
        print(f"Loading initial user data from {user_fixture_path}...")
        try:
            with open(user_fixture_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                users_to_create = data.get("users", [])
                for user_data in users_to_create:
                    username = user_data.get("username")
                    role_code = user_data.get("role_code")
                    name = user_data.get("role_name")
                    email = user_data.get("email")
                    is_superuser = user_data.get("is_superuser", 0)
                    if not username or not role_code:
                        print(
                            f"Warning: Skipping user with username '{username}' due to missing username or role_code."
                        )
                        continue
                    try:
                        role, created = Role.objects.get_or_create(
                            role_code=role_code,
                            defaults={"name": name, "description": name},
                        )
                        if created:
                            print(f"Created Role: '{role_code}' with name '{name}'")
                        if is_superuser:
                            user, created_user = User.objects.get_or_create(
                                username=username,
                                defaults={
                                    "email": email,
                                    "is_superuser": True,
                                    "is_staff": True,
                                },
                            )
                            if created_user:
                                user.set_password("12345678")
                                user.save()
                        else:
                            user, created_user = User.objects.get_or_create(
                                username=username,
                                defaults={
                                    "email": email,
                                    "is_superuser": False,
                                    "is_staff": False,
                                },
                            )
                            if created_user:
                                user.set_password("12345678")
                                user.save()
                        user.role = role
                        user.save(update_fields=["role"])
                        if created_user:
                            print(f"Created User: {username} with Role: {name}")
                        else:
                            print(f"Updated User: {username} with Role: {name}")
                    except IntegrityError as e:
                        print(f"Skipping user '{username}' due to IntegrityError: {e}")
        except Exception as e:
            print(f"Error loading initial users: {e}")
    else:
        print(
            f"Warning: User fixture file '{INIT_USER_JSON}' not found. Skipping user initialization."
        )

    # === SECTION 2: Tải dữ liệu Cấu hình ===
    # Assume this is your concrete model
    ConfigApp = apps.get_model("IT_OAUTH", "ConfigApp")
    config_fixture_path = os.path.join(fixture_dir, INIT_CONFIG_JSON)

    if os.path.exists(config_fixture_path):
        print(f"\nLoading initial config data from {config_fixture_path}...")
        try:
            with open(config_fixture_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                configs_to_create = data.get("configs_app", [])
                for config_data in configs_to_create:
                    name_config = config_data.get("name_config")
                    value = config_data.get("value")
                    status = config_data.get("status", False)
                    # Get the new description field
                    description = config_data.get("description", "")
                    is_used = config_data.get("is_used", False)
                    type_config = config_data.get("type_config")

                    if not name_config:
                        print("Warning: Skipping config due to missing 'name_config'.")
                        continue

                    config, created = ConfigApp.objects.get_or_create(
                        name_config=name_config,
                        defaults={
                            "value": value,
                            "status": status,
                            "description": description,
                            "is_used": is_used,
                            "type_config": type_config,
                        },
                    )
                    if created:
                        print(f"Created Config: {name_config}")
                    else:
                        print(f"Updated Config: {name_config}")

        except Exception as e:
            print(f"Error loading initial configs: {e}")
    else:
        print(
            f"\nWarning: Config fixture file '{INIT_CONFIG_JSON}' not found. Skipping config initialization."
        )
