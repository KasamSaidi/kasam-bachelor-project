from datetime import datetime
import pandas as pd

from sqlalchemy import Column, Integer, String, select, ForeignKey, DateTime, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
from sqlalchemy.types import TypeDecorator
from sqlalchemy import create_engine

db_directory = "sqlite:///data.db"
Base = declarative_base()


def create_base(boolean):
    if boolean:
        engine = create_engine(db_directory)
        Base.metadata.create_all(engine)
        global session
        session = Session(engine)
        global user_id
        user_id = 0
    else:
        engine = create_engine(db_directory)
        Base.metadata.create_all(engine)

def create_webapp_base(webapp_session):
    global session
    session = webapp_session

def webapp_user_session(webapp_user_id):
    global user_id
    user_id = webapp_user_id

class FuelType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value not in ('Petrol', 'Diesel'):
            raise ValueError("Fuel type must be 'petrol' or 'diesel'")
        return value

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)
    manufacturer = Column(String)
    model = Column(String)
    desc = Column(String)
    fuel_type = Column(FuelType)

    def load_cars_from_excel(file_path):
        df = pd.read_excel(file_path)

        accepted_fuel_types = ["Petrol", "Diesel"]
        df = df.loc[df['Fuel Type'].isin(accepted_fuel_types)]

        for _, row in df.iterrows():
            vehicle = Vehicle(
                model=row['Model'],
                manufacturer=row['Manufacturer'],
                desc=row['Description'],
                fuel_type=row['Fuel Type'],
            )
            session.add(vehicle)
        session.commit()

    def add_vehicles(request):
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
        session.add(custom_car_entry)
        session.commit()

    def get_vehicles():
        vehicles = session.query(Vehicle).all()
        return vehicles

    def get_object_from_str(vehicles, select_vehicle_str):
        for vehicle in vehicles:
            vehicle_str = vehicle.manufacturer + ' ' + vehicle.model + ' ' + vehicle.desc
            if select_vehicle_str == vehicle_str:
                return vehicle
        return

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    points = relationship("Point", back_populates="user")
    badges = relationship("Badge", back_populates="user")
    statistics = relationship("Statistic", back_populates="user")

    def __init__(self, name: str, password: str):
        self.name = name
        self.hashed_password = password

        self.create_default_statistics()

    def create_default_statistics(self):

        if not self.statistics:

            default_statistics = Statistic(
                user=self,
                routes_driven=0,
                eco_routes_driven=0,
                saved_emissions=0,
                km_driven=0
            )
            session.add(default_statistics)
            session.commit()

    def modify_statistics(self, routes_driven=None, eco_routes_driven=None, saved_emissions=None, km_driven=None):
        if not self.statistics:
            raise ValueError("User has no statistics.")

        user_statistics = self.statistics[0]

        if routes_driven is not None:
            user_statistics.routes_driven += routes_driven
        if eco_routes_driven is not None:
            user_statistics.eco_routes_driven += eco_routes_driven
        if saved_emissions is not None:
            user_statistics.saved_emissions += saved_emissions
        if km_driven is not None:
            user_statistics.km_driven += km_driven

        session.commit()

    def check_badges(self, distance_driven, emissions_saved, eco_routes_driven):
        now = datetime.now()

        badges = [
            Badge(self, "Gefahrene Kilometer - Bronze", "Gefahrene Kilometer Stufe: Bronze", 10, now),
            Badge(self, "Gefahrene Kilometer - Silber", "Gefahrene Kilometer Stufe: Silber", 100, now),
            Badge(self, "Gefahrene Kilometer - Gold", "Gefahrene Kilometer Stufe: Gold", 1000, now),
            Badge(self, "Gesparte Emissionen - Bronze", "Gesparte Emissionen (gramm) Stufe: Bronze", 10, now),
            Badge(self, "Gesparte Emissionen - Silber", "Gesparte Emissionen (gramm) Stufe: Silber", 100, now),
            Badge(self, "Gesparte Emissionen - Gold", "Gesparte Emissionen (gramm) Stufe: Gold", 1000, now),
            Badge(self, "Eco Routen gefahren - Bronze", "Anzahl gefahrener Eco Routen Stufe: Bronze", 1, now),
            Badge(self, "Eco Routen gefahren - Silber", "Anzahl gefahrener Eco Routen Stufe: Silber", 10, now),
            Badge(self, "Eco Routen gefahren - Gold", "Anzahl gefahrener Eco Routen Stufe: Gold", 100, now),
        ]

        for badge in badges:
            if "Gefahrene Kilometer" in badge.badge_name:
                if distance_driven >= badge.milestones:
                    existing_badge_names = [badge.badge_name for badge in self.badges]
                    if badge.badge_name  in existing_badge_names:
                        continue
                    session.add(badge)
                    session.commit()
                    break

        for badge in badges:
            if "Gesparte Emissionen" in badge.badge_name:
                if emissions_saved >= badge.milestones:
                    existing_badge_names = [badge.badge_name for badge in self.badges]
                    if badge.badge_name  in existing_badge_names:
                        continue
                    session.add(badge)
                    session.commit()
                    break

        for badge in badges:
            if "Eco Routen gefahren" in badge.badge_name:
                if eco_routes_driven >= badge.milestones:
                    existing_badge_names = [badge.badge_name for badge in self.badges]
                    if badge.badge_name  in existing_badge_names:
                        continue
                    session.add(badge)
                    session.commit()
                    break

class Point(Base):
    __tablename__ = 'points'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    points = Column(Integer)
    timestamp = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="points")

class Badge(Base):
    __tablename__ = 'badges'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    badge_name = Column(String)
    description = Column(String)
    milestones = Column(Integer)
    timestamp = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="badges")

    def __init__(self, user: None, badge_name: str, description: str, milestones: int, timestamp: datetime):
        self.user = user
        self.badge_name = badge_name
        self.description = description
        self.milestones = milestones
        self.timestamp = timestamp

class Statistic(Base):
    __tablename__ = 'statistics'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    routes_driven = Column(Integer)
    eco_routes_driven = Column(Integer)
    saved_emissions = Column(Integer)
    km_driven = Column(Integer)

    user = relationship("User", back_populates="statistics")

    def __init__(self, user: None, routes_driven: int, eco_routes_driven: int, saved_emissions: int, km_driven: int):
        self.user = user
        self.routes_driven = routes_driven
        self.eco_routes_driven = eco_routes_driven
        self.saved_emissions = saved_emissions
        self.km_driven = km_driven

def user_mapper(name, password):
    user_mapper.user = User(name, password)
    session.add(user_mapper.user)
    session.commit()
    session.refresh(user_mapper.user)

def get_total_points(username):
    user = session.query(User).filter_by(name=username).first()
    if user:
        total_points = session.query(Point).filter_by(user_id=user.id).first()
        session.refresh(user)
        return total_points.points
    return

def get_stats(username):
    user = session.query(User).filter_by(name=username).first()
    if user:
        statistic = session.query(Statistic).filter_by(user_id=user.id).first()
        session.refresh(user)
        return statistic.km_driven, statistic.saved_emissions, statistic.eco_routes_driven, 
    return

def modify_stats(username, km, route_type, saved_emissions):
    user = session.query(User).filter_by(name=username).first()
    if route_type == 'normal':
        user.modify_statistics(km_driven=km, routes_driven=1)
    elif route_type == 'eco':       
        user.modify_statistics(km_driven=km, eco_routes_driven=1, saved_emissions=saved_emissions)
    session.refresh(user)

def update_badges(username, km_driven, saved_emissions, eco_routes_driven):
    user = session.query(User).filter_by(name=username).first()
    print(km_driven)
    user.check_badges(distance_driven=km_driven, emissions_saved=saved_emissions, eco_routes_driven=eco_routes_driven)
    session.refresh(user)

def get_new_user_badges(username):
    user = session.query(User).filter_by(name=username).first()
    if user:
        current_time = datetime.now()
        user_badges = [badge.badge_name for badge in user.badges if (current_time - badge.timestamp).total_seconds() <= 30]
        session.refresh(user)
        return user_badges
    return []

def add_points(username, points):
    user = session.query(User).filter_by(name=username).first()
    if user:
        new_point = Point(user=user, points=points, timestamp=datetime.now())
        session.add(new_point)
        session.commit()
        session.refresh(user)
        return True
    return False

def add_badge(username, badge_name, description):
    user = session.query(User).filter_by(name=username).first()
    if user:
        new_badge = Badge(user=user, badge_name=badge_name, description=description, milestones=0, timestamp=datetime.now())
        session.add(new_badge)
        session.commit()
        session.refresh(user)
        return True
    return False

# def change_user_points(username, points_change):
#     user = session.query(User).filter_by(name=username).first()
#     if user:
#         user_points = session.query(Point).filter_by(user_id=user.id).first()
#         if user_points:
#             user_points.points += points_change
#         else:
#             new_point = Point(user=user, points=points_change, timestamp=datetime.now())
#             session.add(new_point)
#         session.commit()
#     session.refresh(user)

# def add_user_badge(username, badge_name):
#     user = session.query(User).filter_by(name=username).first()
#     if user:
#         new_badge = Badge(user=user, badge_name=badge_name, description=" ", timestamp=datetime.now())
#         session.add(new_badge)
#         session.commit()
#     session.refresh(user)

# def remove_user_badge(username, badge_name):
#     user = session.query(User).filter_by(name=username).first()
#     if user:
#         badge_to_remove = session.query(Badge).filter_by(user_id=user.id, badge_name=badge_name).first()
#         if badge_to_remove:
#             session.delete(badge_to_remove)
#             session.commit()
#     session.refresh(user)

def get_leaderboard(username, filter):
    if filter == 'points':
        leaderboard = session.query(User, func.sum(Point.points).label('value')).join(Point).group_by(User).order_by(text('value DESC')).all()
    elif filter == 'routes_driven':
        leaderboard = session.query(User, func.sum(Statistic.routes_driven).label('value')).join(Statistic).group_by(User).order_by(text('value DESC')).all()
    elif filter == 'eco_routes_driven':
        leaderboard = session.query(User, func.sum(Statistic.eco_routes_driven).label('value')).join(Statistic).group_by(User).order_by(text('value DESC')).all()
    elif filter == 'saved_emissions':
        leaderboard = session.query(User, func.sum(Statistic.saved_emissions).label('value')).join(Statistic).group_by(User).order_by(text('value DESC')).all()
    else:
        leaderboard = session.query(User, func.sum(Statistic.km_driven).label('value')).join(Statistic).group_by(User).order_by(text('value DESC')).all()

    user = session.query(User).filter_by(name=username).first()

    return leaderboard, user

def check_if_table_empty(table):
    if session.query(table).first():
        return True
    return False

def stmt_results():
    result = session.execute(select(User.id, User.name, User.hashed_password))
    return result

def stmt_result_password(users_id):
    stmt = select(User.hashed_password).where(User.id == users_id)
    result = session.execute(stmt)
    return result
