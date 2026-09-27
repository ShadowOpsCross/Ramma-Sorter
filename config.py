import json
import os
from pathlib import Path


APP_NAME = "RammaSorter"

APP_DATA_DIR = Path(
    os.getenv("APPDATA", Path.home())
) / APP_NAME

CONFIG_FILE = APP_DATA_DIR / "config.json"


def ensure_app_data_dir():
    APP_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


def get_gemini_api_key() -> str | None:
    if not CONFIG_FILE.exists():
        return None

    try:
        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as config_file:
            config = json.load(config_file)

        api_key = config.get(
            "gemini_api_key"
        )

        if not api_key:
            return None

        return api_key.strip()

    except (
        json.JSONDecodeError,
        OSError
    ):
        return None


def save_gemini_api_key(api_key: str):
    ensure_app_data_dir()

    config = {
        "gemini_api_key": api_key.strip()
    }

    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8"
    ) as config_file:
        json.dump(
            config,
            config_file,
            indent=4
        )


def remove_gemini_api_key():
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()