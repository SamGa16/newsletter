from os import path
from json import load, JSONDecodeError
from src.common.path import SLCT_CONFIG_PATH

def load_config(config_path=SLCT_CONFIG_PATH):
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
    if "score_threshold" not in config or not isinstance(config["score_threshold"], int):
        raise ValueError("Invalid configuration: 'score_threshold' must be an int.")
    if "max_news_per_block" not in config or not isinstance(config["max_news_per_block"], int):
        raise ValueError("Invalid configuration: 'max_news_per_block' must be an int.")
    if "patterns_to_remove" not in config or not isinstance(config["patterns_to_remove"], list):
        raise ValueError("Invalid configuration: 'patterns_to_remove' must be a list of removal patterns.")
    if "languages" not in config or not isinstance(config["languages"], dict):
        raise ValueError("Invalid configuration: 'languages' must be a dict of languages definitions.")
    for lang in config["languages"]:
        parameters = config["languages"][lang]
        characters = "characters" not in parameters
        stopwords = "stopwords" not in parameters
        content_blocks = "content_blocks" not in parameters
        if characters or stopwords or content_blocks:
            raise ValueError(f"Invalid language definition: {lang}")