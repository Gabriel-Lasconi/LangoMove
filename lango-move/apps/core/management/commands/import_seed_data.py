from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, call_command, CommandError


class Command(BaseCommand):
    help = "Import application seed data from a JSON fixture into the current database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--input",
            default="seed_data.json",
            help="Fixture filename inside BASE_DIR / fixtures/",
        )

    def handle(self, *args, **options):
        input_name = options["input"]
        fixture_path = Path(settings.BASE_DIR) / "fixtures" / input_name

        if not fixture_path.exists():
            raise CommandError(f"Fixture file not found: {fixture_path}")

        self.stdout.write(self.style.NOTICE(f"Importing seed data from: {fixture_path}"))

        call_command("loaddata", str(fixture_path))

        self.stdout.write(self.style.SUCCESS("Seed data imported successfully."))