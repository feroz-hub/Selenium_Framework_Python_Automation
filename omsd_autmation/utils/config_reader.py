import os
import yaml

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
    def get(cls, key, default=None):
        config = cls.load_config()
        keys = key.split(".")

        value = config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                # already reached a final value (string, int, bool, etc.)
                break

        return value if value is not None else default
