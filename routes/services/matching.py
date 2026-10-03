import difflib
import re

from routes.models import FuelStation


class FuelStationMatcher:
    US_STATES = {
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE",
        "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS",
        "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
        "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY",
        "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
        "WI", "WY",
    }

    def normalize(self, value):
        if value is None:
            return ""

        value = str(value).upper()
        value = re.sub(r"[^A-Z0-9\s]", " ", value)
        value = re.sub(r"\s+", " ", value)

        return value.strip()

    def match(self, stations):
        matched_stations = []

        for station in stations:
            properties = station.get("properties", {})

            name = self.normalize(properties.get("name"))
            city = self.normalize(properties.get("city"))
            state = self.normalize(properties.get("state_code"))
            address = self.normalize(
                properties.get("address_line1")
            )

            if not name or state not in self.US_STATES:
                continue

            candidates = FuelStation.objects.filter(
                state=state,
                city__iexact=city,
            )

            if not candidates.exists():
                candidates = FuelStation.objects.filter(
                    state=state
                )

            best_match = None
            best_score = 0

            for candidate in candidates:
                candidate_name = self.normalize(
                    candidate.name
                )
                candidate_address = self.normalize(
                    candidate.address
                )
                candidate_city = self.normalize(
                    candidate.city
                )

                name_score = difflib.SequenceMatcher(
                    None,
                    name,
                    candidate_name,
                ).ratio()

                address_score = 0

                if address and candidate_address:
                    address_score = difflib.SequenceMatcher(
                        None,
                        address,
                        candidate_address,
                    ).ratio()

                city_score = (
                    1.0
                    if city == candidate_city
                    else 0
                )

                score = (
                    name_score * 0.65
                    + address_score * 0.20
                    + city_score * 0.15
                )

                if score > best_score:
                    best_score = score
                    best_match = candidate

            if best_match and best_score >= 0.60:
                matched_stations.append(
                    {
                        "station": best_match,
                        "price": float(
                            best_match.retail_price
                        ),
                        "match_score": round(
                            best_score,
                            3,
                        ),
                        "geoapify_name": name,
                        "feature": station,
                    }
                )

        return matched_stations
