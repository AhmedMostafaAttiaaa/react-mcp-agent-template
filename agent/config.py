import yaml
from dotenv import load_dotenv


def load_config(path: str = "config.yaml") -> dict:
    """Loads .env into the environment, then parses config.yaml."""
    load_dotenv()
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
