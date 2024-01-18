from flask import Flask, render_template, request, jsonify
from routing.elevation import get_elevation_data
from routing.traffic import get_traffic_flow
from routing.routing_processing import create_route_instance, geocode_location

app = Flask(__name__)

vehicles = ["VW Golf", "Toyota Camry", "Ford Mustang", "Tesla Model 3"]


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
            route_instance = create_route_instance(route_type='eco', start_coordinates=start_coordinates, end_coordinates=end_coordinates)

            geojson_data, route_data = route_instance.calculate_route()

            traffic_flow_data = get_traffic_flow(route_data['routes'][0]['legs'][0]['points'])

            get_elevation_data(route_data)

            return render_template('routing_result.html', start_location=start_address, end_location=end_address,
                                   start_coordinates=start_coordinates, end_coordinates=end_coordinates,
                                   geojson_data=geojson_data, route_data=route_data, traffic_flow_data=traffic_flow_data)
        else:
            return render_template('routing_result.html', start_location=start_address, end_location=end_address,
                                   start_coordinates=None, end_coordinates=None, geojson_data=None,
                                   route_data=None, traffic_flow_data=None)
    except Exception as e:
        print(f"Error calculating route: {e}")
        return jsonify({"error": "Error calculating route"}), 500

if __name__ == '__main__':
    app.run(debug=True)
