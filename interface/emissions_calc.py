from .hbefa_interface import get_result_table

def get_emissions(fuel_type, traffic_situations, street_lengths):
    emissions = []
    emissions_dict = {"CO": 0, "CO2": 0, "FC": 0, "HC": 0,"Methan": 0, "mKr": 0, "Nox": 0, "Pb": 0, "PM": 0}
    concepts = ["CO", "CO2", "FC", "HC","Methan", "mKr", "Nox", "Pb", "PM"]

    for concept in concepts:
        for traffic_situation in traffic_situations:
            emissions.append(get_result_table(concept, fuel_type, traffic_situation))

        emissions_dict = calculate_emission(concept, emissions_dict, emissions, street_lengths)

        emissions.clear()

    return emissions_dict

def calculate_emission(concept, emissions_dict, emissions, street_lengths):
    total_emission = 0

    for i in range(len(street_lengths)):
        emission_per_km = emissions[i][0]
        street_length_km = street_lengths[i] / 1000
        emission = emission_per_km * street_length_km

        total_emission += emission
        emissions_dict[concept] = total_emission

    return emissions_dict
