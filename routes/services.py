import difflib
import math
import re
import time

import requests
from django.conf import settings

from .models import FuelStation


class RoutingService:
    GEOCODING_URL = "https://api.geoapify.com/v1/geocode/search"
    ROUTING_URL = "https://api.geoapify.com/v1/routing"
    PLACES_URL = "https://api.geoapify.com/v2/places"

    MAX_RANGE_MILES = 500
    MPG = 10

    def get_fuel_stations_along_route(self, geometry):
        start_time = time.time()

        simplified_geometry = self._simplify_geometry(geometry)

        coordinates = [
            [point["lon"], point["lat"]]
            for point in simplified_geometry
        ]

        response = requests.post(
            self.PLACES_URL,
            params={
                "apiKey": settings.GEOAPIFY_API_KEY,
            },
            json={
                "categories": ["service.vehicle.fuel"],
                "filter": {
                    "type": "polyline",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": coordinates,
                    },
                    "buffer": 1000,
                },
                "limit": 50,
            },
            timeout=20,
        )

        print(
            f"Places API took: {time.time() - start_time:.2f}s"
        )

        if not response.ok:
            print(
                "GEOAPIFY PLACES ERROR:",
                response.text,
            )

        response.raise_for_status()

        return response.json().get("features", [])

    def normalize_text(self, value):
        if value is None:
            return ""

        value = str(value).upper()

        # Remove punctuation.
        value = re.sub(r"[^A-Z0-9\s]", " ", value)

        # Collapse multiple spaces.
        value = re.sub(r"\s+", " ", value)

        return value.strip()

    def match_station_to_database(self, station):
        properties = station.get("properties", {})

        poi_name = self.normalize_text(
            properties.get("name")
        )

        poi_city = self.normalize_text(
            properties.get("city")
        )

        poi_state = self.normalize_text(
            properties.get("state_code")
        )

        poi_address = self.normalize_text(
            properties.get("address_line1")
        )

        if not poi_name or not poi_state:
            return None

        # The assessment is for routes inside the USA.
        # The provided CSV also contains Canadian provinces,
        # so only allow US state codes here.
        us_states = {
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE",
            "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS",
            "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
            "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY",
            "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
            "WI", "WY",
        }

        if poi_state not in us_states:
            return None

        # First try to narrow candidates by state + city.
        candidates = FuelStation.objects.filter(
            state=poi_state,
            city__iexact=properties.get("city", ""),
        )

        # If no station exists in that city, search the whole state.
        if not candidates.exists():
            candidates = FuelStation.objects.filter(
                state=poi_state
            )

        best_match = None
        best_score = 0

        for candidate in candidates:
            candidate_name = self.normalize_text(
                candidate.name
            )

            candidate_address = self.normalize_text(
                candidate.address
            )

            candidate_city = self.normalize_text(
                candidate.city
            )

            name_score = difflib.SequenceMatcher(
                None,
                poi_name,
                candidate_name,
            ).ratio()

            address_score = 0

            if poi_address and candidate_address:
                address_score = difflib.SequenceMatcher(
                    None,
                    poi_address,
                    candidate_address,
                ).ratio()

            city_score = (
                1.0
                if poi_city == candidate_city
                else 0
            )

            # Station name is the strongest signal.
            score = (
                name_score * 0.65
                + address_score * 0.20
                + city_score * 0.15
            )

            if score > best_score:
                best_score = score
                best_match = candidate

        # Reject weak matches rather than inventing a price.
        if best_match is None or best_score < 0.60:
            return None

        return {
            "station": best_match,
            "match_score": round(best_score, 3),
            "geoapify_name": properties.get("name"),
        }

    def get_matched_fuel_stations(self, fuel_stations):
        matched = []

        for station in fuel_stations:
            match = self.match_station_to_database(station)

            if match:
                fuel_station = match["station"]

                matched.append(
                    {
                        "station": fuel_station,
                        "price_per_gallon": float(
                            fuel_station.retail_price
                        ),
                        "match_score": match["match_score"],
                        "geoapify_name": match["geoapify_name"],
                    }
                )

        return matched

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

        data = response.json()

        results = data.get("results", [])

        if not results:
            raise ValueError("No route found.")

        route = results[0]

        fuel_stations = self.get_fuel_stations_along_route(
            route["geometry"]
        )

        matched_stations = self.get_matched_fuel_stations(
            fuel_stations
        )

        return {
            "distance_miles": route["distance"] / 1609.344,
            "duration_minutes": route["time"] / 60,
            "fuel_station_count": len(fuel_stations),
            "matched_station_count": len(matched_stations),
            "fuel_stations": [
                {
                    "station": item["station"].name,
                    "city": item["station"].city,
                    "state": item["station"].state,
                    "price_per_gallon": item[
                        "price_per_gallon"
                    ],
                    "match_score": item["match_score"],
                }
                for item in matched_stations
            ],
            "geometry": self._simplify_geometry(
                route["geometry"]
            ),
        }

    def _simplify_geometry(self, geometry):
        coordinates = geometry[0]

        max_points = 250

        if len(coordinates) <= max_points:
            return coordinates

        step = math.ceil(
            len(coordinates) / max_points
        )

        simplified = coordinates[::step]

        # Always keep the final point.
        if simplified[-1] != coordinates[-1]:
            simplified.append(coordinates[-1])

        return simplified
