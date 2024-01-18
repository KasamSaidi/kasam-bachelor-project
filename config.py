import yaml

def load_config(filename="config.yaml"):
    with open(filename, "r") as f:
        config = yaml.safe_load(f)
    return config

config = load_config()

TOMTOM_API_KEY = config.get('TOMTOM_API_KEY')
