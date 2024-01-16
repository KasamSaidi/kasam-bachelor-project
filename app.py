from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

vehicles = ["VW Golf", "Toyota Camry", "Ford Mustang", "Tesla Model 3"]

TOMTOM_API_KEY = '1n7hfspttTjYk53H8xAeOcNM53cseplD'
OPENELEVATION_API_URL = 'https://api.open-elevation.com/api/v1/lookup'
OPENTOPODATA_HEALTH_URL = 'https://api.opentopodata.org/health'
OPENTOPODATA_API_URL = 'https://api.opentopodata.org/v1/srtm90m'

def is_opentopodata_available():
    try:
        response = requests.get(OPENTOPODATA_HEALTH_URL)
        print('health:', response)
        return response.ok

    except requests.RequestException:
        return False

def geocode_location(location):  # eigene klasse oder file
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

def get_traffic_flow(points):  # loop durch alle points um traffic fuer alle straßen zu kriegen
    try:
        traffic_api_url = 'https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json'
        start_point = points[0]
        point_str = "{},{}".format(start_point['latitude'], start_point['longitude'])

        traffic_api_params = {
            'key': TOMTOM_API_KEY,
            'point': point_str
        }
        response = requests.get(traffic_api_url, params=traffic_api_params)

        traffic_flow_data = response.json().get('flowSegmentData', {})
        return traffic_flow_data

    except Exception as e:
        print(f"Error fetching traffic flow data: {e}")
        return {"error": "Error fetching traffic flow data"}

def get_elevation_data_opentopodata(points):  # eigene klasse oder file
    try:
        data = {
            "locations": "|".join([f"{point['latitude']},{point['longitude']}" for point in points]),
            "interpolation": "cubic"
        }

        response = requests.post(OPENTOPODATA_API_URL, json=data)
        elevation_data = response.json()
        return elevation_data

    except Exception as e:
        print(f"Error fetching Opentopo Elevation data: {e}")
        return {"error": "Error fetching Opentopo Elevation data"}

def get_elevation_data_openelevation(points):
    try:
        response = requests.post(
            OPENELEVATION_API_URL,
            json={"locations": [{"latitude": point["latitude"], "longitude": point["longitude"]} for point in points]}
        )

        elevation_data = response.json()
        return elevation_data

    except Exception as e:
        print(f"Error fetching Open Elevation data: {e}")
        return {"error": "Error fetching Open Elevation data"}

def calculate_route(start_coordinates, end_coordinates):  # eigene klasse oder file
    url = f'https://api.tomtom.com/routing/1/calculateRoute/{start_coordinates}:{end_coordinates}/json'
    params = {'key': TOMTOM_API_KEY}
    eco_params = {'key': TOMTOM_API_KEY, 'routeType': 'eco'}
    response = requests.get(url, params=params)
    route_data = response.json()

    eco_response = requests.get(url, params=eco_params)
    eco_route_data = eco_response.json()
    if route_data.get('routes') and eco_route_data.get('routes'):
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

        eco_geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        for route in eco_route_data['routes']:
            for leg in route['legs']:
                eco_coordinates = [[point['longitude'], point['latitude']] for point in leg['points']]
                eco_feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": eco_coordinates
                    }
                }
                eco_geojson['features'].append(eco_feature)
        return geojson, eco_geojson, route_data, eco_route_data
    else:
        return None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/routing')
def routing_input_handler():
    return render_template('routing.html', vehicles=vehicles)

@app.route('/calculate_route', methods=['POST'])
def calculate_route_handler():
    try:
        start_location = request.form.get('start_location')
        end_location = request.form.get('end_location')

        start_coordinates, start_address = geocode_location(start_location)
        end_coordinates, end_address = geocode_location(end_location)

        if start_coordinates and end_coordinates:
            geojson_data, eco_geojson_data, eco_route_data, route_data = calculate_route(start_coordinates, end_coordinates)

            traffic_flow_data = get_traffic_flow(route_data['routes'][0]['legs'][0]['points'])
            use_opentopodata = is_opentopodata_available()
            if use_opentopodata:
                elevation_data = get_elevation_data_opentopodata(route_data['routes'][0]['legs'][0]['points'])
            else:
                elevation_data = get_elevation_data_openelevation(route_data['routes'][0]['legs'][0]['points'])

            print(elevation_data)
            return render_template('routing_result.html', start_location=start_address, end_location=end_address,
                                   start_coordinates=start_coordinates, end_coordinates=end_coordinates,
                                   geojson_data=geojson_data, route_data=route_data, eco_geojson_data=eco_geojson_data,
                                   eco_route_data=eco_route_data, traffic_flow_data=traffic_flow_data)
        else:
            return render_template('routing_result.html', start_location=start_address, end_location=end_address,
                                   start_coordinates=None, end_coordinates=None, geojson_data=None, route_data=None, eco_geojson_data=None,
                                   eco_route_data=None, traffic_flow_data=None)
    except Exception as e:
        print(f"Error calculating route: {e}")
        return jsonify({"error": "Error calculating route"}), 500

if __name__ == '__main__':
    app.run(debug=True)
