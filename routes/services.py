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

        data = response.json()
        results = data.get("results", [])

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
            timeout=15,
        )

        response.raise_for_status()

        return response.json()