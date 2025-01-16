from os import path
from json import load, JSONDecodeError
from src.common.path import RDCT_CONFIG_PATH

def load_config(config_path=RDCT_CONFIG_PATH):
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
    if "summarization_model" not in config or not isinstance(config["summarization_model"], str):
        raise ValueError("Invalid configuration: 'summarization_model' must be a string of LLM name.")
    if "translator_model" not in config or not isinstance(config["translator_model"], str):
        raise ValueError("Invalid configuration: 'translator_model' must be a string of LLM name.")