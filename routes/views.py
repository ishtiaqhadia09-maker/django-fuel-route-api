from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RouteRequestSerializer
from .services.routing import RoutingService
from .services.fuel import FuelStationService
from .services.matching import FuelStationMatcher
from .services.optimizer import FuelOptimizer


class RouteAPIView(APIView):

    def post(self, request):
        serializer = RouteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        start = serializer.validated_data["start"]
        finish = serializer.validated_data["finish"]

        # 1. Get route between start and finish
        routing_service = RoutingService()
        route = routing_service.get_route(
            start=start,
            finish=finish,
        )

        # 2. Find fuel stations along the route
        fuel_service = FuelStationService()
        stations = fuel_service.get_stations(route["geometry"])

        # 3. Match API stations with stations from the provided dataset
        matcher = FuelStationMatcher()
        matched_stations = matcher.match(stations)

        # 4. Calculate each station's position on the route
        optimizer = FuelOptimizer()
        positioned_stations = optimizer.add_route_positions(
            matched_stations,
            route["geometry"],
        )

        # 5. Select cost-effective fuel stops
        fuel_stops = optimizer.optimize(
            route_distance=route["distance_miles"],
            stations=positioned_stations,
        )

        # 6. Calculate fuel cost
        fuel_cost = optimizer.calculate_cost(
            route_distance=route["distance_miles"],
            stops=fuel_stops,
        )

        return Response(
            {
                "route": {
                    "start": start,
                    "finish": finish,
                    "distance_miles": round(
                        route["distance_miles"],
                        2,
                    ),
                    "duration_minutes": round(
                        route["duration_minutes"],
                        2,
                    ),
                },

                "fuel": {
                    "mpg": optimizer.MPG,
                    "gallons_purchased": fuel_cost["gallons_purchased"],
                    "total_cost": fuel_cost["total_cost"],
                },

                "fuel_stops": [
                    {
                        "station": stop["station"].name,
                        "city": stop["station"].city,
                        "state": stop["station"].state,
                        "price_per_gallon": stop["price"],
                        "distance_from_start_miles": (
                            stop["distance_from_start"]
                        ),
                    }
                    for stop in fuel_stops
                ],

                "map": {
                    "geometry": route["geometry"],
                },
            }
        )