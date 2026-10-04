import math


class FuelOptimizer:
    MAX_RANGE_MILES = 500
    MPG = 10

    @property
    def TANK_CAPACITY_GALLONS(self):
        return self.MAX_RANGE_MILES / self.MPG

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates in miles."""

        earth_radius = 3958.8

        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1)
            * math.cos(lat2)
            * math.sin(dlon / 2) ** 2
        )

        c = 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a),
        )

        return earth_radius * c

    def add_route_positions(self, stations, route_geometry):
        """
        Add the approximate distance of each station
        from the beginning of the route.
        """

        route_points = [
            (point["lat"], point["lon"])
            for point in route_geometry
        ]

        cumulative_distances = [0]

        for index in range(1, len(route_points)):
            previous = route_points[index - 1]
            current = route_points[index]

            segment_distance = self.calculate_distance(
                previous[0],
                previous[1],
                current[0],
                current[1],
            )

            cumulative_distances.append(
                cumulative_distances[-1] + segment_distance
            )

        positioned_stations = []

        for item in stations:
            properties = item["feature"]["properties"]

            station_lat = properties.get("lat")
            station_lon = properties.get("lon")

            if station_lat is None or station_lon is None:
                continue

            closest_index = 0
            closest_distance = float("inf")

            for index, (lat, lon) in enumerate(route_points):
                distance = self.calculate_distance(
                    station_lat,
                    station_lon,
                    lat,
                    lon,
                )

                if distance < closest_distance:
                    closest_distance = distance
                    closest_index = index

            positioned_stations.append(
                {
                    "station": item["station"],
                    "price": item["price"],
                    "distance_from_start": round(
                        cumulative_distances[closest_index],
                        2,
                    ),
                }
            )

        return sorted(
            positioned_stations,
            key=lambda station: station["distance_from_start"],
        )

    def optimize(self, route_distance, stations):
        """
        Find the minimum-cost sequence of fuel stops.

        Assumptions:
        - Vehicle starts with a full 50-gallon tank.
        - Vehicle gets 10 miles per gallon.
        - Maximum range is 500 miles.
        - At every selected station, the tank is refilled to full.
        - Initial fuel is free because its purchase price is unknown.

        The cost of reaching a fuel station is based on the
        amount of fuel consumed since the previous stop, using
        the current station's price because that is where the
        tank is refilled.
        """

        stations = sorted(
            stations,
            key=lambda station: station["distance_from_start"],
        )

        # Keep the cheapest station when multiple stations
        # have the same approximate route position.
        unique_stations = {}

        for station in stations:
            position = station["distance_from_start"]

            if (
                position not in unique_stations
                or station["price"]
                < unique_stations[position]["price"]
            ):
                unique_stations[position] = station

        stations = list(unique_stations.values())

        start = {
            "station": None,
            "price": None,
            "distance_from_start": 0,
        }

        destination = {
            "station": None,
            "price": None,
            "distance_from_start": route_distance,
        }

        nodes = [start] + stations + [destination]

        # cost[i] = cheapest cost to reach node i.
        costs = [float("inf")] * len(nodes)

        # previous[i] = previous node used to reach node i.
        previous = [None] * len(nodes)

        # Starting with a full tank means reaching the
        # first station uses free initial fuel.
        costs[0] = 0

        for index in range(1, len(nodes)):
            current_node = nodes[index]
            current_position = current_node["distance_from_start"]

            for previous_index in range(index):
                previous_node = nodes[previous_index]
                previous_position = (
                    previous_node["distance_from_start"]
                )

                distance = current_position - previous_position

                # Invalid or unreachable segment.
                if distance <= 0:
                    continue

                if distance > self.MAX_RANGE_MILES:
                    continue

                # Destination does not require a fuel purchase.
                if current_node["station"] is None:
                    travel_cost = 0
                else:
                    gallons_used = distance / self.MPG
                    travel_cost = (
                        gallons_used * current_node["price"]
                    )

                new_cost = (
                    costs[previous_index]
                    + travel_cost
                )

                if new_cost < costs[index]:
                    costs[index] = new_cost
                    previous[index] = previous_index

        destination_index = len(nodes) - 1

        if costs[destination_index] == float("inf"):
            raise ValueError(
                "No feasible fuel route exists within "
                "the vehicle's 500-mile range."
            )

        # Reconstruct the cheapest path.
        selected_stops = []

        current_index = previous[destination_index]

        while current_index is not None:
            node = nodes[current_index]

            if node["station"] is not None:
                selected_stops.append(node)

            current_index = previous[current_index]

        selected_stops.reverse()

        return selected_stops

    def calculate_cost(self, route_distance, stops):
        """
        Calculate total fuel purchased and total fuel cost.

        Assumptions:
        - Vehicle starts with a full 50-gallon tank.
        - Vehicle gets 10 miles per gallon.
        - At each selected stop, the tank is refilled to full.
        - Initial fuel is free because its purchase price is unknown.
        """

        tank_capacity = self.TANK_CAPACITY_GALLONS

        total_gallons = 0
        total_cost = 0

        current_position = 0
        current_fuel = tank_capacity

        for stop in stops:
            distance_to_stop = (
                stop["distance_from_start"]
                - current_position
            )

            if distance_to_stop <= 0:
                continue

            fuel_used = distance_to_stop / self.MPG

            if fuel_used > current_fuel:
                raise ValueError(
                    "Selected fuel stops are not reachable "
                    "within the vehicle's fuel range."
                )

            current_fuel -= fuel_used

            # Refill the tank to its full capacity.
            gallons_to_buy = (
                tank_capacity - current_fuel
            )

            total_gallons += gallons_to_buy

            total_cost += (
                gallons_to_buy * stop["price"]
            )

            current_fuel = tank_capacity
            current_position = (
                stop["distance_from_start"]
            )

        # Make sure the vehicle can reach the destination
        # using the fuel remaining after the final stop.
        remaining_distance = (
            route_distance - current_position
        )

        remaining_fuel_needed = (
            remaining_distance / self.MPG
        )

        if remaining_fuel_needed > current_fuel:
            raise ValueError(
                "Final fuel stop does not provide enough "
                "range to reach the destination."
            )

        return {
            "gallons_purchased": round(
                total_gallons,
                2,
            ),
            "total_cost": round(
                total_cost,
                2,
            ),
        }