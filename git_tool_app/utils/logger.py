import logging
import json
from datetime import datetime
from git_tool_app.utils.config import CONFIG_DIR, load_config

class JsonFormatter(logging.Formatter):
    """Custom formatter to output logs as JSON strings."""
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Capture tracebacks natively if an exception occurs
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)

def get_logger(name="gta"):
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.DEBUG)
    config = load_config()

    # Determine if we are in dev/debug mode
    is_debug = config.get("debug", False) or config.get("environment") == "development"

    # 1. Console Handler: Output for the terminal UI
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.DEBUG if is_debug else logging.INFO)
    
    # If in debug mode, add a prefix so you know which file is printing the log
    if is_debug:
        c_handler.setFormatter(logging.Formatter('[%(levelname)s] %(module)s: %(message)s'))
    else:
        c_handler.setFormatter(logging.Formatter('%(message)s'))
        
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    # 2. File Handler: JSONL output for deep debugging (Appends to ~/.gta/gta.log)
    log_file = CONFIG_DIR / "gta.log"
    f_handler = logging.FileHandler(log_file, encoding="utf-8")
    f_handler.setLevel(logging.DEBUG)  # The file ALWAYS captures everything
    f_handler.setFormatter(JsonFormatter())

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger