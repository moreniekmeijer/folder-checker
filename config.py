import json
import os

CONFIG_FILE = os.path.expanduser("~/Library/Application Support/folder-cleaner/config.json")
os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

DEFAULTS = {
    "WATCH_PATHS": ["~/Downloads"],
    "MAX_SIZE_MB": 5000,
    "MAX_AMOUNT_FILES": 20,
    "MAX_INTERACTIVE_FILES": 10,
    "CHECK_INTERVAL_SEC": 300,
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULTS.copy()
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
