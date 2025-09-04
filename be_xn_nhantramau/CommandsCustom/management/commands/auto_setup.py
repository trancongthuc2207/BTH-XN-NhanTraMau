from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Automatically run required setup commands"

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.WARNING("Starting setup..."))

            self.stdout.write(self.style.NOTICE(
                "Running makemigrations for IT_OAUTH"))
            call_command("makemigrations", "IT_OAUTH")

            self.stdout.write(self.style.NOTICE(
                "Running migrate IT_OAUTH on 'oauth' database"))
            call_command("migrate", "IT_OAUTH", database="oauth")

            self.stdout.write(self.style.NOTICE(
                "Running makemigrations ALL App"))
            call_command("makemigrations")
            call_command("migrate")

            self.stdout.write(self.style.SUCCESS(
                "✅ All commands executed successfully!"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Error occurred: {e}"))
