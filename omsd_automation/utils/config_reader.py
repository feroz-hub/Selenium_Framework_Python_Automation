import os

import yaml

from pathlib import Path


class Config:
    _config = None

    @classmethod
    def load_config(cls, path="config.yaml"):
        if cls._config is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_path = os.path.join(base_dir, path)
            with open(config_path, "r") as f:
                cls._config = yaml.safe_load(f)
        return cls._config

    @classmethod
    def get_env(cls):
        config = cls.load_config()
        return config.get("env", "staging")  # default = staging

    @classmethod
    def get(cls, key, default=None):
        env = cls.get_env()
        config = cls.load_config()
        # First go into environments.<env>
        value = config.get("environments", {}).get(env, {})
        # Traverse keys like "users.software_uploader.username"
        for k in key.split("."):
            if isinstance(value, dict):
                value = value.get(k)
            else:
                break
        return value if value is not None else default

    @classmethod
    def get_user(cls, role):
        """Return username/password dict for a given role (e.g. software_uploader)."""
        return cls.get(f"users.{role}")

