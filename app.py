from flask import Flask, render_template, request
import requests

app = Flask(__name__)

TOMTOM_API_KEY = '1n7hfspttTjYk53H8xAeOcNM53cseplD'

def geocode_location(location):
    url = f'https://api.tomtom.com/search/2/geocode/{location}.json'
    params = {'key': TOMTOM_API_KEY}
    response = requests.get(url, params=params)
    data = response.json()

    if data.get('results'):
        address = data['results'][0]['address']
        coordinates = data['results'][0]['position']
        return f'{coordinates["lat"]},{coordinates["lon"]}', address['freeformAddress']
    else:
        return None

def calculate_route(start_coordinates, end_coordinates):
    url = f'https://api.tomtom.com/routing/1/calculateRoute/{start_coordinates}:{end_coordinates}/json'
    params = {'key': TOMTOM_API_KEY}
    response = requests.get(url, params=params)
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
    else:
        return None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate_route', methods=['POST'])
def calculate_route_handler():
    start_location = request.form.get('start_location')
    end_location = request.form.get('end_location')

    start_coordinates, start_address = geocode_location(start_location)
    end_coordinates, end_address = geocode_location(end_location)

    if start_coordinates and end_coordinates:
        geojson_data, route_data = calculate_route(start_coordinates, end_coordinates)
        return render_template('result.html', start_location=start_address, end_location=end_address,
                               start_coordinates=start_coordinates, end_coordinates=end_coordinates,
                               geojson_data=geojson_data, route_data=route_data)
    else:
        return render_template('result.html', start_location=start_address, end_location=end_address,
                               start_coordinates=None, end_coordinates=None, geojson_data=None, route_data=None)

@app.route('/map')
def show_map():
    return render_template('map.html')

if __name__ == '__main__':
    app.run(debug=True)
