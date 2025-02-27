import os
from pathlib import Path

import yaml


class ConfigManager:
    """Manages application configuration following XDG standards"""

    def __init__(self):
        self.config = {}
        self.load_config()

    def load_config(self):
        """Load config from XDG standard locations"""
        # Check XDG_CONFIG_HOME first
        config_home = os.environ.get(
            "XDG_CONFIG_HOME", os.path.expanduser("~/.config")
        )

        config_paths = [
            Path(config_home) / "orakle/orakle.yaml",
            Path("/etc/orakle/orakle.yaml"),
            Path("config/orakle.yaml"),  # Fallback to repo config
        ]

        for config_path in config_paths:
            if config_path.exists():
                with open(config_path) as f:
                    self.config = (
                        yaml.safe_load(f) or {}
                    )  # Ensure config is a dict

                    # Add default audio configuration if not present
                    if "audio" not in self.config:
                        self.config["audio"] = {}
                    if "buffer_size_mb" not in self.config["audio"]:
                        self.config["audio"]["buffer_size_mb"] = 10

                    return

        # If no config file found, create minimal default config
        self.config = {"audio": {"buffer_size_mb": 10}}

    def get(self, key_path: str, default=None):
        """Get a config value using dot notation"""
        keys = key_path.split(".")
        value = self.config

        for key in keys:
            try:
                value = value[key]
            except (KeyError, TypeError):
                return default

        return value


# Global config instance
config = ConfigManager()
