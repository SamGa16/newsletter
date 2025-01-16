from os import path
from json import load, JSONDecodeError
from src.common.path import DSGN_CONFIG_PATH

def load_config(config_path=DSGN_CONFIG_PATH):
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
    Validate the structure of the selection configuration file.
    """
    if "logs" not in config or not isinstance(config["logs"], str):
        raise ValueError("Invalid configuration: 'logs' must be a string of file name.")
    if "paths" not in config or not isinstance(config["paths"], dict):
        raise ValueError("Invalid configuration: 'paths' must be a dict of strings for paths.")
    if "html_parts" not in config or not isinstance(config["html_parts"], dict):
        raise ValueError("Invalid configuration: 'html_parts' must be a dict of HTML string configurations.")
    if "sections" not in config or not isinstance(config["sections"], dict):
        raise ValueError("Invalid configuration: 'sections' must be a dict of categories for news.")