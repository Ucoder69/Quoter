import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATE_PATH = BASE_DIR / "data" / "templates.json"


def load_templates():

    if not TEMPLATE_PATH.exists():
        return {}

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_templates(data):

    TEMPLATE_PATH.parent.mkdir(exist_ok=True)

    with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_template(name):

    templates = load_templates()

    if name not in templates:
        raise ValueError("Template not found")

    return templates[name]