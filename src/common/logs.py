from os import makedirs, path
from datetime import datetime
from src.common.path import BASE_DIR

def log_message(message, log_file, logging=True, log_level="INFO"):
    """
    Enhanced logging utility for debugging and tracking operations.
    """
    # Ensure the logs directory exists
    logs_dir = path.join(BASE_DIR, "logs")
    makedirs(logs_dir, exist_ok=True)

    # Format the log entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} [{log_level}] {message}"

    # Log to the file if enabled
    if logging:
        try:
            log_file_path = path.join(logs_dir, f"{log_file}.log")
            with open(log_file_path, "a", encoding="utf-8") as log_f:
                log_f.write(f"{log_entry}\n")
        except Exception as e:
            print(f"Failed to write to log file: {e}")

    # Print the log message to the console
    print(log_entry)