
import requests
import math
# from .export_data.json_export import export_to_json


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

def get_elevation_data(route_data):
    use_opentopodata = is_opentopodata_available()

    progress_points = get_points_from_progress(route_data)

    points = get_points(progress_points)

    if use_opentopodata:
        elevation_data = get_elevation_data_opentopodata(points)
    else:
        elevation_data = get_elevation_data_openelevation(points)

    differences = calculate_elevation_and_distance_difference(progress_points, elevation_data)

    average_slope_percent, average_slope_degrees, total_distance_length = calculate_average_elevation_and_distance(differences)
    print(f"\nAverage Slope Percent: {average_slope_percent}%")
    print(f"Average Slope Degrees: {average_slope_degrees} degrees")
    print(f"Distance Length: {total_distance_length}m")

def get_points_from_progress(route_data):
    try:
        points_data = route_data['routes'][0]['legs'][0]['points']
        progress_data = route_data['routes'][0]['progress']

        result = []

        for progress_entry in progress_data:
            point_index = progress_entry.get("pointIndex")
            distance_in_meters = progress_entry.get("distanceInMeters")

            if point_index is not None and 0 <= point_index < len(points_data):
                point = points_data[point_index]
                result.append({
                    "pointIndex": point_index,
                    "distanceInMeters": distance_in_meters,
                    "point": point
                })

        return result

    except Exception as e:
        print(f"Error processing route data: {e}")
        return []

def get_points(result_data):
    return [entry["point"] for entry in result_data]

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

def calculate_elevation_and_distance_difference(points, elevation_data):
    differences = []

    for i in range(1, len(points)):
        prev_point = points[i - 1]
        current_point = points[i]

        prev_elevation = elevation_data['results'][i - 1]['elevation']
        current_elevation = elevation_data['results'][i]['elevation']

        elevation_diff = current_elevation - prev_elevation
        distance_diff = current_point['distanceInMeters'] - prev_point['distanceInMeters']

        differences.append({
            "pointIndex": i,
            "elevationDifference": elevation_diff,
            "distanceDifference": distance_diff
        })

    return differences

def calculate_elevation_and_distance(elevation_diff, distance_diff):
    slope_percent = (elevation_diff / distance_diff) * 100

    slope_degrees = math.degrees(math.atan(slope_percent / 100))

    slope_degrees_rounded = round(slope_degrees, 4)

    distance_length = math.sqrt(elevation_diff**2 + distance_diff**2)

    return slope_percent, slope_degrees_rounded, distance_length

def calculate_average_elevation_and_distance(points):
    total_slope_percent = 0
    total_slope_degrees = 0
    total_distance_length = 0

    for i in range(0, len(points)):
        elevation_diff = points[i]['elevationDifference']
        distance_diff = points[i]['distanceDifference']

        slope_percent, slope_degrees, distance_length = calculate_elevation_and_distance(elevation_diff, distance_diff)

        total_slope_percent += slope_percent
        total_slope_degrees += slope_degrees
        total_distance_length += distance_length

    if len(points) > 1:
        num_points = len(points) - 1
    num_points = len(points)

    average_slope_percent = total_slope_percent / num_points
    average_slope_degrees = total_slope_degrees / num_points

    return average_slope_percent, round(average_slope_degrees, 4), total_distance_length
