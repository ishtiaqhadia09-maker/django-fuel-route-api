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
        """

        stations = sorted(
            stations,
            key=lambda station: station["distance_from_start"],
        )

        # Remove duplicate stations at the same route position.
        unique_stations = []

        seen_positions = set()

        for station in stations:
            position = station["distance_from_start"]

            if position in seen_positions:
                continue

            seen_positions.add(position)
            unique_stations.append(station)

        # Add the destination as the final node.
        destination = {
            "station": None,
            "price": None,
            "distance_from_start": route_distance,
        }

        nodes = unique_stations + [destination]

        # cost[i] = cheapest cost to reach node i.
        costs = [float("inf")] * len(nodes)

        # previous[i] = previous node used in the cheapest path.
        previous = [None] * len(nodes)

        # Starting point is free because the vehicle
        # starts with a full tank.
        start_position = 0

        for index, node in enumerate(nodes):

            current_position = node["distance_from_start"]

            # Find the cheapest known way to reach this node.
            if index == 0:
                distance_from_start = current_position

                if distance_from_start <= self.MAX_RANGE_MILES:
                    if node["station"] is not None:
                        fuel_needed = (
                            distance_from_start / self.MPG
                        )

                        costs[index] = (
                            fuel_needed * node["price"]
                        )

            # Check every previous reachable node.
            for previous_index in range(index):

                previous_node = nodes[previous_index]

                previous_position = (
                    previous_node["distance_from_start"]
                )

                distance = (
                    current_position - previous_position
                )

                if distance <= 0:
                    continue

                if distance > self.MAX_RANGE_MILES:
                    continue

                # Reaching the destination does not require
                # buying additional fuel.
                if node["station"] is None:
                    travel_cost = 0
                else:
                    gallons_needed = distance / self.MPG
                    travel_cost = (
                        gallons_needed * node["price"]
                    )

                if (
                    costs[previous_index]
                    + travel_cost
                    < costs[index]
                ):
                    costs[index] = (
                        costs[previous_index]
                        + travel_cost
                    )

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
        Calculate fuel purchased and total cost.

        Assumptions:
        - Vehicle starts with a full 50-gallon tank.
        - Fuel economy is 10 miles per gallon.
        - At each selected stop, the vehicle refuels to full.
        - Initial fuel cost is excluded because its price
        is not provided.
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

            fuel_used = (
                distance_to_stop / self.MPG
            )

            current_fuel -= fuel_used

            gallons_to_buy = (
                tank_capacity - current_fuel
            )

            total_gallons += gallons_to_buy

            total_cost += (
                gallons_to_buy * stop["price"]
            )

            # Tank is full again.
            current_fuel = tank_capacity
            current_position = (
                stop["distance_from_start"]
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
