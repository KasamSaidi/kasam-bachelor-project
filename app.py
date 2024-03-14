import os
from typing_extensions import Union
from functools import wraps
from werkzeug import Response

from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, validators, PasswordField
from flask_wtf import FlaskForm

from routing.traffic import get_traffic_flow, select_traffic_points
from routing.routing_processing import create_route_instance, geocode_location
from interface.emissions_calc import get_emissions
from input import bcrypt_passwords
from mapper import orm_mapper
from mapper.orm_mapper import Vehicle, Point, Badge
from login import login

app = Flask(__name__)
app.static_folder = 'static'

file_path = os.path.abspath(os.getcwd()) + "\data.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + file_path
user_id = 0
db = SQLAlchemy(app)


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[validators.Length(min=4, max=25)])
    password = PasswordField("Password", validators=[validators.InputRequired()])

@app.before_request
def setup():
    if os.path.isfile("data.db"):
        boolean = False
        session = db.session
        orm_mapper.create_webapp_base(session)
    else:
        boolean = True
    orm_mapper.create_base(boolean)
    db.Model.metadata.create_all(bind=db.engine)

def is_logged_in(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "username" in session:
            return func(*args, **kwargs)
        return render_template("forbidden.html")
    return wrapper

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Successfully logged out!")
    return render_template("index.html")

@app.route("/register")
def add_user():
    form = RegistrationForm()
    return render_template("registrationform.html", form=form)

@app.route("/login")
def login_user():
    if 'username' in session:
        flash("Sie sind schon eingeloggt.")
    form = RegistrationForm()
    return render_template("loginform.html", form=form)

@app.route("/login_register", methods=["POST"])
def login_register():
    if request.referrer.endswith("/register"):
        return register_user()
    return save_login_user()

def register_user() -> Union[Response, str]:
    username = request.form["username"]
    password = request.form["password"]
    while True:
        if isinstance(login.existing_user_check(username), int):
            flash("Nutzer existiert bereits, versuchen Sie es wieder oder gehen Sie zum login.")
            return redirect(url_for('add_user'))
        else:
            global user_id
            user_id = 0
            orm_mapper.webapp_user_session(user_id)
            hashed_password = bcrypt_passwords.hash_password(password)
            orm_mapper.user_mapper(username, hashed_password)
            orm_mapper.add_badge(username, "Registriert", "Sie haben sich registriert.")
            orm_mapper.add_points(username, 0)
            session["username"] = request.form["username"]
            break

    return render_template("user_dashboard.html", the_username=username)

def save_login_user() -> Union[Response, str]:
    username = request.form["username"]
    password = request.form["password"]
    while True:
        if isinstance(login.existing_user_check(username), int):
            global user_id
            user_id = login.existing_user_check(username)
            orm_mapper.webapp_user_session(user_id)
            if login.password_verification(password, user_id):
                session["username"] = request.form["username"]
                user_points = orm_mapper.get_total_points(session["username"])
                break
            else:
                flash("Falsches Passwort, versuchen Sie es erneut")
                return redirect(url_for('login_user'))
        else:
            flash("Kein Nutzer unter diesem Namen existiert, versuchen Sie es erneut.")
            return redirect(url_for('login_user'))
    return render_template("user_dashboard.html", the_username=username, user_points=user_points)

@app.route("/user/<username>")
@is_logged_in
def user_homepage(username):
    username = session["username"]

    if request:
        if request.referrer.endswith("/calculate_route"):
            route_info = session.get('route_info', {})
            route_type = request.args.get('route_type')
            if route_type == 'normal':
                length_in_km = route_info.get('length_in_km')
                saved_emissions = 0
            else:
                length_in_km = route_info.get('eco_length_in_km')
                saved_emissions = route_info.get('saved_emissions')

            orm_mapper.modify_stats(username, length_in_km, route_type, saved_emissions)
            new_km_driven, new_saved_emissions, new_eco_routes_driven = orm_mapper.get_stats(session["username"])
            orm_mapper.update_badges(username, new_km_driven, new_saved_emissions, new_eco_routes_driven)

    user_points = orm_mapper.get_total_points(session["username"])

    return render_template("user_dashboard.html", the_username=username, user_points=user_points)

@app.route('/user/<username>')
@is_logged_in
def user_profile(username):
    if not orm_mapper.check_if_table_empty(Point) and not orm_mapper.check_if_table_empty(Badge):
        orm_mapper.add_badge(username, badge_name="Registriert")
        orm_mapper.add_points(username, points=0)
    total_points = orm_mapper.get_total_points(username)
    user_badges = orm_mapper.get_user_badges(username)
    return render_template('user_profile.html', total_points=total_points, badges=user_badges)

@app.route('/user/<username>/manage_points', methods=['POST'])
@is_logged_in
def manage_points(username):
    points_change = int(request.form['points'])
    orm_mapper.change_user_points(username, points_change)
    return redirect(url_for('user_profile', username=username))

@app.route('/user/<username>/manage_badges', methods=['POST'])
@is_logged_in
def manage_badges(username):
    badge_name = request.form['badge']
    orm_mapper.add_user_badge(username, badge_name)
    return redirect(url_for('user_profile', username=username))

@app.route('/user/<username>/remove_badges', methods=['POST'])
@is_logged_in
def remove_badges(username):
    badge_name_to_remove = request.form['badge_to_remove']
    orm_mapper.remove_user_badge(username, badge_name_to_remove)
    return redirect(url_for('user_profile', username=username))

@app.route('/user/<username>/leaderboard', methods=['GET', 'POST'])
@is_logged_in
def leaderboard(username):
    filter_criteria = request.args.get('filter_criteria')
    leaderboard, user = orm_mapper.get_leaderboard(username, filter_criteria)

    filter_title_mapping = {
        'points': 'Punkte',
        'routes_driven': 'Anzahl Fahrten',
        'eco_routes_driven': 'Anzahl Eco Fahrten',
        'saved_emissions': 'Gesparte Emissionen (g)',
        'km_driven': 'Kilometer gefahren (km)'
    }

    filter_title = filter_title_mapping.get(filter_criteria, 'Wert')

    return render_template('leaderboard.html', leaderboard=leaderboard, logged_in_user=user, filter_title=filter_title)

@app.route('/routing')
@is_logged_in
def routing_input_handler():
    if not orm_mapper.check_if_table_empty(Vehicle):
        Vehicle.load_cars_from_excel("Euro_6_Latest.xlsx")
    vehicle_entries = Vehicle.get_vehicles()
    return render_template('routing.html', vehicle_entries=vehicle_entries)

@app.route('/add_custom_car', methods=['GET', 'POST'])
@is_logged_in
def add_custom_car():
    if request.method == 'POST':
        Vehicle.add_vehicles(request)
        return redirect(url_for('routing_input_handler'))
    return render_template('add_custom_car.html')

@app.route('/calculate_route', methods=['POST'])
@is_logged_in
def calculate_route_handler():
    try:
        start_location = request.form.get('start_location')
        end_location = request.form.get('end_location')

        selected_vehicle_str = request.form.get('select_vehicle')
        selected_vehicle = Vehicle.get_object_from_str(Vehicle.get_vehicles(), selected_vehicle_str)
        selected_vehicle_str = selected_vehicle.manufacturer + ' ' + selected_vehicle.model + ' ' + selected_vehicle.desc

        start_coordinates, start_address = geocode_location(start_location)
        end_coordinates, end_address = geocode_location(end_location)

        geojson_data, route_data = determine_route("normal", start_coordinates, end_coordinates)
        eco_geojson_data, eco_route_data = determine_route("eco", start_coordinates, end_coordinates)

        length_in_km, travel_time = get_length_travel_time(route_data)
        eco_length_in_km, eco_travel_time = get_length_travel_time(eco_route_data)

        traffic_flow_data, street_lengths = determine_traffic(route_data)
        eco_traffic_flow_data, eco_street_lengths = determine_traffic(eco_route_data)

        emissions = determine_emissions(traffic_flow_data, street_lengths, selected_vehicle)
        eco_emissions = determine_emissions(eco_traffic_flow_data, eco_street_lengths, selected_vehicle)
        saved_emissions = calculate_saved_emissions(emissions, eco_emissions)

        session['route_info'] = {
            'length_in_km': length_in_km,
            'eco_length_in_km': eco_length_in_km,
            'saved_emissions': sum(saved_emissions.values()),
        }

        return render_template('routing_result.html', start_location=start_address, end_location=end_address,
                                geojson_data=geojson_data, length_in_km=length_in_km, travel_time=travel_time,
                                eco_geojson_data=eco_geojson_data, eco_length_in_km=eco_length_in_km,
                                eco_travel_time=eco_travel_time, eco_emissions=eco_emissions,
                                emissions=emissions, saved_emissions=saved_emissions,
                                selected_vehicle=selected_vehicle)
    except Exception as e:
        print(f"Error calculating route: {e}")
        flash("Zu Ihrem gewünschten Start und Ziel Punkt, konnte keine Route ermittelt werden, versuchen sie es erneut.")
        return redirect(url_for('routing_input_handler'))

def determine_route(route_type, start_coordinates, end_coordinates):
    route_instance = create_route_instance(
        route_type=route_type,
        start_coordinates=start_coordinates,
        end_coordinates=end_coordinates
    )

    geojson_data, route_data = route_instance.calculate_route()

    return geojson_data, route_data

def determine_traffic(route_data):
    traffic_points, street_lengths = select_traffic_points(route_data)
    traffic_flow_data = get_traffic_flow(traffic_points)

    return traffic_flow_data, street_lengths

def get_length_travel_time(route_data):
    length = route_data['routes'][0]['summary']['lengthInMeters'] / 1000
    travel_time = route_data['routes'][0]['summary']['travelTimeInSeconds']
    travel_time = round(travel_time / 60)

    return length, travel_time

def determine_emissions(traffic_flow_data, street_lengths, selected_vehicle):
    fuel_type = "B (4T)"
    if selected_vehicle.fuel_type == "Diesel":
        fuel_type = "D"

    emissions = get_emissions(fuel_type, traffic_flow_data, street_lengths)

    return emissions

def calculate_saved_emissions(emissions, eco_emissions):
    saved_emissions = {key: max(0, emissions[key] - eco_emissions.get(key, 0)) for key in emissions}

    return saved_emissions

if __name__ == '__main__':
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY
    # app.run(debug=False)  # End Realese Debug False lassen
    app.run(debug=True)
