from os import path
from json import load, JSONDecodeError
from src.common.path import INIT_CONFIG_PATH

def load_config(config_path=INIT_CONFIG_PATH):
    """
    Load and validate the selection configuration JSON file.
    """
    if not path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as file:
        try:
            config = load(file)
            validate_config(config)
            return config
        except JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON configuration: {e}")

def validate_config(config):
    """
    Validate the structure of the scraping configuration file.
    """
    if "logs" not in config or not isinstance(config["logs"], str):
        raise ValueError("Invalid configuration: 'logs' must be a string of file name.")
    if "paths" not in config or not isinstance(config["paths"], list):
        raise ValueError("Invalid configuration: 'paths' must be a list of strings for paths.")