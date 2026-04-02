import json
import os
import shutil
from typing import Dict, Any

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "data", "config.json")
BACKUP_PATH = os.path.join(BASE_DIR, "data", "config_backup.json")

ALLOWED_GST = [12, 18]
ALLOWED_TYPES = ["room", "cottage"]


class ConfigError(Exception):
    pass


class ConfigManager:

    def __init__(self, path: str = CONFIG_PATH):
        self.path = path
        self._ensure_environment()
        self.config = self._load_config()

    # ----------------------------
    # Environment setup
    # ----------------------------
    def _ensure_environment(self):

        os.makedirs("data", exist_ok=True)

        if not os.path.exists(self.path):
            self._create_default_config()

    def _create_default_config(self):

        default_config = {
            "settings": {
                "currency_symbol": "₹",
                "backup_enabled": True
            },
            "units": {
                "00_": {
                    "display_name": "Sample Room",
                    "type": "room",
                    "base_price": 3000,
                    "default_adults": 2,
                    "max_adults": 2,
                    "max_children": 1,
                    "gst_percent": 12,
                    "extra_mattress_price": {
                        "child_under_5_free": True,
                        "child_price_under_12": 500,
                        "adult_price": 800
                    }
                }
            }
        }

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)

    # ----------------------------
    # Load / Save
    # ----------------------------
    def _load_config(self):
        # print("DEBUG", self.path)
        if not os.path.exists(self.path):
            self._create_default_config()

        if os.path.getsize(self.path) == 0:
            self._create_default_config()

        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._validate_structure(data)

        return data


    def save(self):

        if self.config.get("settings", {}).get("backup_enabled", True):
            self._backup()

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def _backup(self):

        if os.path.exists(self.path):
            shutil.copy(self.path, BACKUP_PATH)

    # ----------------------------
    # Validation
    # ----------------------------
    def _validate_structure(self, data):

        if "settings" not in data:
            raise ConfigError("Missing settings section")

        if "units" not in data or not isinstance(data["units"], dict):
            raise ConfigError("Units must be a dictionary")

        seen_names = []

        for unit_id, unit in data["units"].items():

            if not unit_id:
                raise ConfigError("Unit ID cannot be empty")

            self._validate_unit(unit_id, unit)

            name = unit["show_name"]

            if name in seen_names:
                raise ConfigError(f"Duplicate show_name: {name}")

            seen_names.append(name)

    def _validate_unit(self, unit_id, unit):

        required = [
            "parser_key",
            "show_name",
            "type",
            "base_price",
            "default_adults",
            "max_adults",
            "max_children",
            "gst_percent",
            "extra_mattress_price"
        ]

        for field in required:
            if field not in unit:
                raise ConfigError(f"{field} missing in unit {unit_id}")

        if unit["type"] not in ALLOWED_TYPES:
            raise ConfigError(f"Invalid type in {unit_id}")

        if unit["gst_percent"] not in ALLOWED_GST:
            raise ConfigError(f"GST must be 12 or 18 in {unit_id}")

        if not isinstance(unit["extra_mattress_price"], dict):
            raise ConfigError("extra_mattress_price must be dict")

    # ----------------------------
    # Getters
    # ----------------------------
    def get_all_units(self):
        return self.config["units"]

    def get_parser_keys(self):
        return[u["parser_key"] for u in self.config["units"].values()]
    def get_unit(self, unit_id):
        return self.config["units"].get(unit_id)

    def get_settings(self):
        return self.config["settings"]

    # ----------------------------
    # ID Generator
    # ----------------------------
    def generate_unit_id(self):

        existing = self.config["units"].keys()

        i = 0
        while True:

            candidate = f"{i:02d}_"

            if candidate not in existing:
                return candidate

            i += 1

    # ----------------------------
    # Update Units
    # ----------------------------
    def add_unit(self, unit_data):

        unit_id = self.generate_unit_id()

        self._validate_unit(unit_id, unit_data)

        self.config["units"][unit_id] = unit_data

        self.save()

        return unit_id

    def update_unit(self, unit_id, unit_data):

        if unit_id not in self.config["units"]:
            raise ConfigError("Unit not found")

        self._validate_unit(unit_id, unit_data)

        self.config["units"][unit_id] = unit_data

        self.save()

    def delete_unit(self, unit_id):

        if unit_id in self.config["units"]:
            del self.config["units"][unit_id]
            self.save()

    # ----------------------------
    # Settings
    # ----------------------------
    def update_settings(self, new_settings):

        self.config["settings"].update(new_settings)

        self.save()