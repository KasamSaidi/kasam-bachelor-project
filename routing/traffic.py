
from config import TOMTOM_API_KEY
import requests
import pandas as pd

excel_file = 'routing/traffic_situations.XLSX'

def select_traffic_points(route_data):
    traffic_points = []
    street_lengths = []
    for route in route_data['routes']:
        for instruction in route['guidance']['instructions']:
            point = {
                'latitude': instruction['point']['latitude'],
                'longitude': instruction['point']['longitude'],
                'street': instruction.get('street', instruction.get('roadNumbers', 'N/A'))
            }
            street_lengths.append(instruction['routeOffsetInMeters'])
            traffic_points.append(point)
    street_lengths = street_lenght_processing(street_lengths)
    return traffic_points, street_lengths

def street_lenght_processing(street_lengths):
    calculated_length = []

    for i in range(len(street_lengths)-1):
        calculated_length.append(street_lengths[i+1] - street_lengths[i])
    return calculated_length

def traffic_flow_processing(frc_list, free_flow_speeds):
    frc_mapping = {
        "FRC0": ("AB-Nat.", "AB-City"),
        "FRC1": ("FernStr-Nat.",),
        "FRC2": ("FernStr-City", "HVS",),
        "FRC3": ("FernStr-City.", "HVS",),
        "FRC4": ("Sammel", "Erschliessung"),
        "FRC5": ("Sammel", "Erschliessung"),
        "FRC6": ("Sammel", "Erschliessung"),
    }

    traffic_flow = []

    for frc, free_flow_speed in zip(frc_list, free_flow_speeds):
        if free_flow_speed < 30:
            speed_limit = 30
        else:
            speed_limit = ((free_flow_speed + 9) // 10) * 10

        road_types = frc_mapping.get(frc, ("Unknown",))
        if frc in ("FRC4", "FRC5", "FRC6") and speed_limit > 50:
            road_types = ("Sammel",)

        if frc in ("FRC2", "FRC3") and not (50 <= speed_limit <= 90):
            road_types = ("HVS",)

        traffic_flow.extend([(road_type, speed_limit) for road_type in road_types])
        road_types = [item[0] for item in traffic_flow]
        speed_limits = [item[1] for item in traffic_flow]

    return road_types, speed_limits

def determine_traffic_status(street_types, speed_limits, current_speeds):
    df = pd.read_excel(excel_file)

    agglo_rows = df[df['TS'].str.startswith('Agglo')]

    traffic_flow = []

    for street_type, speed_limit, current_speed in zip(street_types, speed_limits, current_speeds):
        closest_pkw_speed = float('inf')
        traffic_status = "dicht"

        for _, row in agglo_rows.iterrows():
            ts_parts = row['TS'].split('/')
            if len(ts_parts) >= 4:
                row_street_type = ts_parts[1]
                row_speed_limit = int(ts_parts[2])
                row_traffic_status = ts_parts[3]

                if row_street_type == street_type and row_speed_limit == speed_limit:
                    diff = abs(row['PKW'] - current_speed)

                    if diff < closest_pkw_speed:
                        closest_pkw_speed = diff
                        traffic_status = row_traffic_status

        traffic_flow.append("Agglo" + "/" + street_type + "/" + str(speed_limit) + "/" + traffic_status)
    return traffic_flow

def get_traffic_flow(points):
    try:
        traffic_api_url = 'https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/10/json'
        street_names = []
        street_types = []
        current_speeds = []
        free_flow_speeds = []
        for point in points:
            point_str = "{},{}".format(point['latitude'], point['longitude'])
            traffic_api_params = {
                'key': TOMTOM_API_KEY,
                'point': point_str
            }
            response = requests.get(traffic_api_url, params=traffic_api_params)
            traffic_flow_data = response.json().get('flowSegmentData', {})

            street_names.append(point['street'])
            street_types.append(traffic_flow_data['frc'])
            current_speeds.append(traffic_flow_data['currentSpeed'])
            free_flow_speeds.append(traffic_flow_data['freeFlowSpeed'])

        street_types, speed_limits = traffic_flow_processing(street_types, free_flow_speeds)

        traffic_flow_data = determine_traffic_status(street_types, speed_limits, current_speeds)
        return traffic_flow_data

    except Exception as e:
        print(f"Error fetching traffic flow data: {e}")
        return {"error": "Error fetching traffic flow data"}
