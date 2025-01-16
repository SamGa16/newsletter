from os import makedirs, path
from src.agent0_config.config import load_config
from src.common.logs import log_message
from src.common.path import get_full_path

class NewsConfigurator:
    def __init__(self, log_path=None):
        self.config = load_config()
        if log_path:
            self.logs = log_path
        else:
            self.logs = self.config["logs"]

    def create_dirs(self):
        """
        Create directories specified in the configuration if they do not exist.
        """
        # List of directories to create
        dirs_to_create = self.config["paths"]

        # Create each directory if it doesn't exist
        for dir_path in dirs_to_create:
            full_path = get_full_path(dir_path)
            if not path.exists(full_path):
                makedirs(full_path, exist_ok=True)
                log_message(f"Directory created: {full_path}", self.logs)
                if "assets" in dir_path:
                    log_message(f"Potential relevant code might be no available if directory {dir_path} was just created.", 
                                self.logs, log_level="WARNING")
            else:
                log_message(f"Directory already exists: {full_path}", self.logs)
            
    def run_configurator(self):
        """
        Main method to configure the directories for the Newsletter.
        """
        print("Creating directories for the Newsletter...", self.logs)
        self.create_dirs()

        log_message("Newsletter configuration complete.", self.logs)