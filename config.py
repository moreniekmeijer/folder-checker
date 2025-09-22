import json
import os

CONFIG_FILE = os.path.expanduser("~/Library/Application Support/FolderChecker/config.json")
os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

DEFAULTS = {
    "WATCH_PATHS": ["~/Downloads", "~/Desktop"],
    "MAX_SIZE_MB": 2000,
    "MAX_AMOUNT_ITEMS": 20,
    "MAX_INTERACTIVE_FILES": 1000,
    "CHECK_INTERVAL_SEC": 86400,
    "FIRST_RUN_DONE": False
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
