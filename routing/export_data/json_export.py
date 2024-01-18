import json

def export_to_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=2)
