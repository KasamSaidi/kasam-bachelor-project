
import requests

TOMTOM_API_KEY = '1n7hfspttTjYk53H8xAeOcNM53cseplD'


def get_traffic_flow(points):
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
