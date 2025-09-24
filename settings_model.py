import config

INTERVAL_OPTIONS = {
    "Every 5 minutes": 300,
    "Every hour": 3600,
    "Every day": 86400,
    "Every week": 604800,
    "Every month": 2592000,
}


class SettingsModel:
    def __init__(self):
        self.cfg = config.load_config()

    def get(self, key, default=None):
        return self.cfg.get(key, default)

    def set(self, key, value):
        self.cfg[key] = value
        self.save()

    def save(self):
        config.save_config(self.cfg)

    def all(self):
        return self.cfg.copy()
