"""Management command to load initial product fixtures."""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load initial product fixtures (categories and products)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture",
            type=str,
            default="initial_products",
            help="Fixture filename to load (default: initial_products)",
        )

    def handle(self, *args, **options):
        fixture = options["fixture"]
        try:
            call_command("loaddata", f"{fixture}")
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Successfully loaded fixture: "{fixture}"',
                ),
            )
        except Exception as e:  # noqa: BLE001
            self.stdout.write(
                self.style.ERROR(f"✗ Error loading fixture: {e!s}"),
            )
