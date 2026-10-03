import time
from concurrent.futures import ThreadPoolExecutor

import requests
from django.conf import settings


class FuelStationService:
    PLACES_URL = "https://api.geoapify.com/v2/places"

    def _get_stations_for_section(self, coordinates):
        response = requests.post(
            self.PLACES_URL,
            params={
                "apiKey": settings.GEOAPIFY_API_KEY,
            },
            json={
                "categories": [
                    "service.vehicle.fuel"
                ],
                "filter": {
                    "type": "polyline",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": coordinates,
                    },
                    "buffer": 1000,
                },
                "limit": 100,
                "offset": 0,
            },
            timeout=20,
        )

        response.raise_for_status()

        return response.json().get(
            "features",
            []
        )

    def get_stations(self, geometry):
        start_time = time.time()

        coordinates = [
            [point["lon"], point["lat"]]
            for point in geometry
        ]

        # Split the route into 3 sections.
        total_points = len(coordinates)
        section_size = total_points // 3

        sections = [
            coordinates[:section_size + 1],
            coordinates[section_size:2 * section_size + 1],
            coordinates[2 * section_size:],
        ]

        # Query all 3 sections concurrently.
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(
                executor.map(
                    self._get_stations_for_section,
                    sections,
                )
            )

        # Combine results.
        all_stations = []

        for stations in results:
            all_stations.extend(stations)

        # Remove duplicate places.
        unique_stations = {}
        
        for station in all_stations:
            properties = station.get("properties", {})

            place_id = (
                properties.get("place_id")
                or (
                    properties.get("lat"),
                    properties.get("lon"),
                    properties.get("name"),
                )
            )

            unique_stations[place_id] = station

        print(
            f"Places API took: "
            f"{time.time() - start_time:.2f}s"
        )

        return list(unique_stations.values())
