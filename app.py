from flask import Flask, render_template, request, jsonify, url_for, redirect
from routing.elevation import get_elevation_data
from routing.traffic import get_traffic_flow
from routing.routing_processing import create_route_instance, geocode_location
from profile.vehicle import Vehicle

app = Flask(__name__)

vehicle_entries = Vehicle.load_cars_from_excel('Euro_6_Latest.xlsx')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/routing')
def routing_input_handler():
    return render_template('routing.html', vehicle_entries=vehicle_entries)

@app.route('/add_custom_car', methods=['GET', 'POST'])
def add_custom_car():
    if request.method == 'POST':
        custom_manufacturer = request.form.get('custom_manufacturer')
        custom_model = request.form.get('custom_model')
        custom_fuel_type = request.form.get('custom_fuel_type')
        custom_model_desc = request.form.get('custom_model_desc')

        custom_car_entry = Vehicle(
            model=custom_model,
            manufacturer=custom_manufacturer,
            desc=custom_model_desc,
            fuel_type=custom_fuel_type,
        )
        vehicle_entries.append(custom_car_entry)

        return redirect(url_for('routing_input_handler'))

    return render_template('add_custom_car.html')

@app.route('/calculate_route', methods=['POST'])
def calculate_route_handler():
    try:
        start_location = request.form.get('start_location')
        end_location = request.form.get('end_location')

        selected_vehicle_str = request.form.get('select_vehicle')
        selected_vehicle = Vehicle.get_object_from_str(vehicle_entries, selected_vehicle_str)

        start_coordinates, start_address = geocode_location(start_location)
        end_coordinates, end_address = geocode_location(end_location)

        if start_coordinates and end_coordinates:
            route_instance = create_route_instance(route_type='eco', start_coordinates=start_coordinates, end_coordinates=end_coordinates)

            geojson_data, route_data = route_instance.calculate_route()

            traffic_flow_data = get_traffic_flow(route_data['routes'][0]['legs'][0]['points'])

            get_elevation_data(route_data)

            return render_template('routing_result.html', start_location=start_address, end_location=end_address,
                                   start_coordinates=start_coordinates, end_coordinates=end_coordinates,
                                   geojson_data=geojson_data, route_data=route_data, traffic_flow_data=traffic_flow_data,
                                   selected_vehicle=selected_vehicle)
        else:
            return render_template('routing_result.html', start_location=start_address, end_location=end_address,
                                   start_coordinates=None, end_coordinates=None, geojson_data=None,
                                   route_data=None, traffic_flow_data=None)
    except Exception as e:
        print(f"Error calculating route: {e}")
        return jsonify({"error": "Error calculating route"}), 500

if __name__ == '__main__':
    app.run(debug=True)
