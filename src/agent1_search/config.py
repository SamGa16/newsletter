from os import path
from json import load, JSONDecodeError
from src.common.path import SCRP_CONFIG_PATH

def load_config(config_path=SCRP_CONFIG_PATH):
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
    if "paths" not in config or not isinstance(config["paths"], dict):
        raise ValueError("Invalid configuration: 'paths' must be a dict of strings for paths.")
    if "http_requests" not in config or not isinstance(config["http_requests"], dict):
        raise ValueError("Invalid configuration: 'http_requests' must be a dict of connection definitions.")
    if "sites" not in config or not isinstance(config["sites"], list):
        raise ValueError("Invalid configuration: 'sites' must be a list of site definitions.")
    for site in config["sites"]:
        name = "name" not in site
        url = "url" not in site
        news_container = "news_container" not in site
        link_tag = "link_tag" not in site
        link_attr = "link_attr" not in site
        if name or url or news_container or link_tag or link_attr:
            raise ValueError(f"Invalid site definition: {site}")