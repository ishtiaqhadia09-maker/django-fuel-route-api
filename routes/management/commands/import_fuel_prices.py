import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from routes.models import FuelStation


class Command(BaseCommand):
    help = "Import fuel station prices from CSV"

    def handle(self, *args, **options):
        file_path = Path("data/fuel-prices-for-be-assessment.csv")
        with file_path.open(
            newline="", encoding="utf-8-sig"
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                FuelStation.objects.create(
                    station_id=row["OPIS Truckstop ID"],
                    name=row["Truckstop Name"],
                    address=row["Address"],
                    city=row["City"],
                    state=row["State"],
                    rack_id=row["Rack ID"],
                    retail_price=row["Retail Price"],
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Fuel station data imported successfully."
            )
        )