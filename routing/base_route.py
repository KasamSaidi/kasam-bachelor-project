
import requests
from config import TOMTOM_API_KEY


class BaseRoute:
    def __init__(self, start_coordinates, end_coordinates):
        self.params = {
            'key': TOMTOM_API_KEY,
            'extendedRouteRepresentation': 'distance',
            'instructionsType': 'coded',
        }
        self.start_coordinates = start_coordinates
        self.end_coordinates = end_coordinates

    def calculate_route(self):
        routing_api_url = f'https://api.tomtom.com/routing/1/calculateRoute/{self.start_coordinates}:{self.end_coordinates}/json'
        response = requests.get(routing_api_url, params=self.params)
        route_data = response.json()

        if route_data.get('routes'):
            geojson = {
                "type": "FeatureCollection",
                "features": []
            }
            for route in route_data['routes']:
                for leg in route['legs']:
                    coordinates = [[point['longitude'], point['latitude']] for point in leg['points']]
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": coordinates
                        }
                    }
                    geojson['features'].append(feature)
            return geojson, route_data
        return None, None
