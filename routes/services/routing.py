import math
import requests

from django.conf import settings


class RoutingService:
    GEOCODING_URL = "https://api.geoapify.com/v1/geocode/search"
    ROUTING_URL = "https://api.geoapify.com/v1/routing"

    def geocode(self, location):
        response = requests.get(
            self.GEOCODING_URL,
            params={
                "text": location,
                "filter": "countrycode:us",
                "format": "json",
                "limit": 1,
                "apiKey": settings.GEOAPIFY_API_KEY,
            },
            timeout=30,
        )

        response.raise_for_status()

        results = response.json().get("results", [])

        if not results:
            raise ValueError(
                f"Could not find location: {location}"
            )

        result = results[0]

        return result["lat"], result["lon"]

    def get_route(self, start, finish):
        start_lat, start_lon = self.geocode(start)
        finish_lat, finish_lon = self.geocode(finish)

        response = requests.get(
            self.ROUTING_URL,
            params={
                "waypoints": (
                    f"{start_lat},{start_lon}|"
                    f"{finish_lat},{finish_lon}"
                ),
                "mode": "drive",
                "format": "json",
                "apiKey": settings.GEOAPIFY_API_KEY,
            },
            timeout=20,
        )

        response.raise_for_status()

        results = response.json().get("results", [])

        if not results:
            raise ValueError("No route found.")

        route = results[0]

        return {
            "distance_miles": route["distance"] / 1609.344,
            "duration_minutes": route["time"] / 60,
            "geometry": self.simplify_geometry(
                route["geometry"]
            ),
            "raw_geometry": route["geometry"],
        }

    def simplify_geometry(self, geometry):
        coordinates = geometry[0]

        max_points = 250

        if len(coordinates) <= max_points:
            return coordinates

        step = math.ceil(
            len(coordinates) / max_points
        )

        simplified = coordinates[::step]

        if simplified[-1] != coordinates[-1]:
            simplified.append(coordinates[-1])

        return simplified