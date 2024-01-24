
import pandas as pd


class Vehicle:
    def __init__(self, model, manufacturer, desc, fuel_type):
        self.model = model
        self.manufacturer = manufacturer
        self.desc = desc
        self.fuel_type = fuel_type

    def get_manufacturer(self):
        return self.manufacturer

    def get_model(self):
        return self.model

    def load_cars_from_excel(file_path):
        df = pd.read_excel(file_path)
        vehicles = []

        for _, row in df.iterrows():
            vehicle = Vehicle(
                model=row['Model'],
                manufacturer=row['Manufacturer'],
                desc=row['Description'],
                fuel_type=row['Fuel Type'],
            )
            vehicles.append(vehicle)

        return vehicles

    def get_object_from_str(vehicles, select_vehicle_str):
        for vehicle in vehicles:
            vehicle_str = vehicle.manufacturer + ' ' + vehicle.model + ' ' + vehicle.desc
            if select_vehicle_str == vehicle_str:
                return vehicle
        return
