from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = "Export application seed data from the local database into a JSON fixture."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="seed_data.json",
            help="Output fixture filename inside BASE_DIR / fixtures/",
        )

    def handle(self, *args, **options):
        output_name = options["output"]
        fixtures_dir = Path(settings.BASE_DIR) / "fixtures"
        fixtures_dir.mkdir(parents=True, exist_ok=True)

        output_path = fixtures_dir / output_name

        self.stdout.write(self.style.NOTICE(f"Exporting seed data to: {output_path}"))

        with output_path.open("w", encoding="utf-8") as fixture_file:
            call_command(
                "dumpdata",
                "curriculum",
                "users.user",
                "users.classparticipation",
                indent=2,
                natural_foreign=True,
                natural_primary=False,
                stdout=fixture_file,
            )

        self.stdout.write(self.style.SUCCESS(f"Seed data exported successfully to {output_path}"))