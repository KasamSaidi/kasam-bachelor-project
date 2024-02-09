import os
from typing_extensions import Union
from functools import wraps
from werkzeug import Response

from flask import Flask, render_template, request, jsonify, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, validators, PasswordField
from flask_wtf import FlaskForm

# from routing.elevation import get_elevation_data
from routing.traffic import get_traffic_flow, select_traffic_points
from routing.routing_processing import create_route_instance, geocode_location
from profile.vehicle import Vehicle
from input import bcrypt_passwords
from mapper import orm_mapper
from login import login

app = Flask(__name__)
app.static_folder = 'static'

file_path = os.path.abspath(os.getcwd()) + "\data.db"  # "\data.db"
vehicle_entries = Vehicle.load_cars_from_excel('Euro_6_Latest.xlsx')
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
                break
            else:
                flash("Falsches Passwort, versuchen Sie es erneut")
                return redirect(url_for('login_user'))
        else:
            flash("Kein Nutzer unter diesem Namen existiert, versuchen Sie es erneut.")
            return redirect(url_for('login_user'))
    return render_template("user_dashboard.html", the_username=username)

@app.route('/routing')
@is_logged_in
def routing_input_handler():
    return render_template('routing.html', vehicle_entries=vehicle_entries)

@app.route('/add_custom_car', methods=['GET', 'POST'])
@is_logged_in
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
@is_logged_in
def calculate_route_handler():
    try:
        start_location = request.form.get('start_location')
        end_location = request.form.get('end_location')

        selected_vehicle_str = request.form.get('select_vehicle')
        selected_vehicle = Vehicle.get_object_from_str(vehicle_entries, selected_vehicle_str)

        start_coordinates, start_address = geocode_location(start_location)
        end_coordinates, end_address = geocode_location(end_location)

        if start_coordinates and end_coordinates:
            eco_route_instance = create_route_instance(route_type='eco', start_coordinates=start_coordinates, end_coordinates=end_coordinates)
            route_instance = create_route_instance(route_type='normal', start_coordinates=start_coordinates, end_coordinates=end_coordinates)

            geojson_data, route_data = route_instance.calculate_route()
            eco_geojson_data, eco_route_data = eco_route_instance.calculate_route()

            traffic_points = select_traffic_points(route_data)
            traffic_flow_data = get_traffic_flow(traffic_points)  # Für Eco-Routing auch

            # get_elevation_data(route_data)

            return render_template('routing_result.html', start_location=start_address, end_location=end_address,
                                   start_coordinates=start_coordinates, end_coordinates=end_coordinates,
                                   geojson_data=geojson_data, route_data=route_data,
                                   eco_geojson_data=eco_geojson_data, eco_route_data=eco_route_data,
                                   traffic_flow_data=traffic_flow_data, selected_vehicle=selected_vehicle)
        else:
            return render_template('routing_result.html', start_location=start_address, end_location=end_address,
                                   start_coordinates=None, end_coordinates=None, geojson_data=None,
                                   route_data=None, traffic_flow_data=None)
    except Exception as e:
        print(f"Error calculating route: {e}")
        return jsonify({"error": "Error calculating route"}), 500

if __name__ == '__main__':
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.run(debug=True)
