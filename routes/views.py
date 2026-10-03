from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RouteRequestSerializer
from .services import RoutingService


class RouteAPIView(APIView):

    def post(self, request):
        serializer = RouteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        start = serializer.validated_data["start"]
        finish = serializer.validated_data["finish"]

        routing_service = RoutingService()

        route_data = routing_service.get_route(
            start=start,
            finish=finish,
        )

        return Response(route_data)