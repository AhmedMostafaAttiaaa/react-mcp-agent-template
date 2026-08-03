import yaml
from dotenv import load_dotenv


def load_config(path: str = "config.yaml") -> dict:
    load_dotenv()
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
