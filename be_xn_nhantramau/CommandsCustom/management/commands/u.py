from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Automatically run required setup commands"

    def handle(self, *args, **options):
        try:
            call_command("migrate")
            self.stdout.write(self.style.SUCCESS(
                "✅ Migrate commands executed successfully!"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Error occurred: {e}"))
