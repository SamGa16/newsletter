from os import path

# Define function to find main
def find_main_folder(start_path, marker_file="README.md"):
    """
    Traverse upward from the start_path to find the main folder of the project.
    """
    current_path = path.abspath(start_path)

    while True:
        # Check if the marker file exists in the current path
        if path.exists(path.join(current_path, marker_file)):
            return current_path

        # Move up one directory
        parent_path = path.dirname(current_path)

        # If we've reached the root and haven't found the marker file, exit
        if current_path == parent_path:
            return None

        current_path = parent_path

BASE_DIR = find_main_folder(__file__, marker_file="README.md")

def get_full_path(relative_path, base_dir=BASE_DIR):
    return path.join(base_dir, relative_path)

# Define paths for the project
CONFIG_PATH = path.join(BASE_DIR, "configs")
INIT_CONFIG_PATH = path.join(CONFIG_PATH, "config.json")
SCRP_CONFIG_PATH = path.join(CONFIG_PATH, "scraping_config.json")
SLCT_CONFIG_PATH = path.join(CONFIG_PATH, "selection_config.json")
RDCT_CONFIG_PATH = path.join(CONFIG_PATH, "redaction_config.json")
DSGN_CONFIG_PATH = path.join(CONFIG_PATH, "design_config.json")