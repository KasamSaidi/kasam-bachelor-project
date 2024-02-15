
# import pandas as pd

# from sqlalchemy import Column, Integer, String
# from sqlalchemy.types import TypeDecorator
# from mapper.orm_mapper import Base, session

# class FuelType(TypeDecorator):
#     impl = String

#     def process_bind_param(self, value, dialect):
#         if value not in ('petrol', 'diesel'):
#             raise ValueError("Fuel type must be 'petrol' or 'diesel'")
#         return value

# class Vehicle(Base):
#     __tablename__ = "vehicles"

#     id = Column(Integer, primary_key=True)
#     manufacturer = Column(String)
#     model = Column(String)
#     fuel_type = Column(FuelType)
#     weight = Column(Integer, default=None)

#     def load_cars_from_excel(file_path):
#         df = pd.read_excel(file_path)

#         for _, row in df.iterrows():
#             vehicle = Vehicle(
#                 model=row['Model'],
#                 manufacturer=row['Manufacturer'],
#                 desc=row['Description'],
#                 fuel_type=row['Fuel Type'],
#             )
#             session.add(vehicle)
#         session.commit()

#     def add_vehicles(request):
#         custom_manufacturer = request.form.get('custom_manufacturer')
#         custom_model = request.form.get('custom_model')
#         custom_fuel_type = request.form.get('custom_fuel_type')
#         custom_model_desc = request.form.get('custom_model_desc')

#         custom_car_entry = Vehicle(
#             model=custom_model,
#             manufacturer=custom_manufacturer,
#             desc=custom_model_desc,
#             fuel_type=custom_fuel_type,
#         )
#         session.add(custom_car_entry)
#         session.commit()

#     def get_vehicles():
#         return session.query(Vehicle).all()

#     def get_object_from_str(vehicles, select_vehicle_str):
#         for vehicle in vehicles:
#             vehicle_str = vehicle.manufacturer + ' ' + vehicle.model + ' ' + vehicle.desc
#             if select_vehicle_str == vehicle_str:
#                 return vehicle
#         return
