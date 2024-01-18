
from config import TOMTOM_API_KEY
from .base_route import BaseRoute
from .eco_route import EcoRoute
import requests


def geocode_location(location):
    url = f'https://api.tomtom.com/search/2/geocode/{location}.json'
    params = {'key': TOMTOM_API_KEY}
    response = requests.get(url, params=params)
    data = response.json()

    if data.get('results'):
        address = data['results'][0]['address']
        coordinates = data['results'][0]['position']
        return f'{coordinates["lat"]},{coordinates["lon"]}', address['freeformAddress']
    return None

def create_route_instance(route_type, start_coordinates, end_coordinates):
    if route_type == 'eco':
        return EcoRoute(start_coordinates, end_coordinates)
    else:
        return BaseRoute(start_coordinates, end_coordinates)
