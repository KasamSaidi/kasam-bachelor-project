
import requests


OPENELEVATION_API_URL = 'https://api.open-elevation.com/api/v1/lookup'
OPENTOPODATA_HEALTH_URL = 'https://api.opentopodata.org/health'
OPENTOPODATA_API_URL = 'https://api.opentopodata.org/v1/srtm90m'

def is_opentopodata_available():
    try:
        response = requests.get(OPENTOPODATA_HEALTH_URL)
        print('Health:', response)
        return response.ok

    except requests.RequestException:
        return False

def get_elevation_data_opentopodata(points):
    try:
        if len(points) <= 100:
            data = {
                "locations": "|".join([f"{point['latitude']},{point['longitude']}" for point in points]),
                "interpolation": "cubic"
            }
        else:
            reduced_points = [points[0], points[-1]]
            data = {
                "locations": "|".join([f"{point['latitude']},{point['longitude']}" for point in reduced_points]),
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
