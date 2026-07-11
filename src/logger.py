import logging
import os
from datetime import datetime

# Create logs directory if not exists
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Unique log file per run (date + time)
LOG_FILE = os.path.join(LOGS_DIR, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")

# Configure root logger
logging.basicConfig(
    filename=LOG_FILE,
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filemode="w"   # overwrite file each run
)

# Add console handler for live output
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(console_handler)

def get_logger(name: str):
    """Return a logger instance with both file and console output."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger

# Example usage
if __name__ == "__main__":
    logger = get_logger(__name__)
    logger.info("Logger initialized successfully")
    try:
        raise ValueError("Simulated error")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        # Force flush all handlers
        for handler in logging.getLogger().handlers:
            handler.flush()
