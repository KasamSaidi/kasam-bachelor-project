
from .base_route import BaseRoute, TOMTOM_API_KEY


class EcoRoute(BaseRoute):
    def __init__(self, start_coordinates, end_coordinates):
        super().__init__(start_coordinates, end_coordinates)
        self.params = {'key': TOMTOM_API_KEY, 'extendedRouteRepresentation': 'distance', 'routeType': 'eco'}
