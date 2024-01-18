
from config import TOMTOM_API_KEY
from .base_route import BaseRoute


class EcoRoute(BaseRoute):
    def __init__(self, start_coordinates, end_coordinates):
        super().__init__(start_coordinates, end_coordinates)
        self.params = {'key': TOMTOM_API_KEY, 'extendedRouteRepresentation': 'distance', 'routeType': 'eco'}
