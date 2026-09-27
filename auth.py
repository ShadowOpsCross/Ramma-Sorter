import os
import json
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/youtube"
]


APP_NAME = "RammaSorter"

APP_DATA_DIR = Path(
    os.getenv("APPDATA", Path.home())
) / APP_NAME

CREDENTIALS_FILE = APP_DATA_DIR / "client_secret.json"
TOKEN_FILE = APP_DATA_DIR / "token.json"


def ensure_app_data_dir():
    APP_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


def has_credentials() -> bool:
    return CREDENTIALS_FILE.exists()


def is_authenticated() -> bool:
    if not TOKEN_FILE.exists():
        return False

    try:
        credentials = Credentials.from_authorized_user_file(
            str(TOKEN_FILE),
            SCOPES
        )

        return (
            credentials.valid
            or credentials.refresh_token is not None
        )

    except Exception:
        return False


def validate_credentials_file(content: bytes) -> bool:
    try:
        data = json.loads(
            content.decode("utf-8")
        )

        installed = data.get("installed")

        if not installed:
            return False

        required_fields = [
            "client_id",
            "client_secret",
            "auth_uri",
            "token_uri"
        ]

        return all(
            field in installed
            for field in required_fields
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
        AttributeError
    ):
        return False


def save_credentials(content: bytes):
    ensure_app_data_dir()

    with open(
        CREDENTIALS_FILE,
        "wb"
    ) as credentials_file:
        credentials_file.write(content)


def authenticate():
    ensure_app_data_dir()

    credentials = None

    if TOKEN_FILE.exists():
        try:
            credentials = Credentials.from_authorized_user_file(
                str(TOKEN_FILE),
                SCOPES
            )

        except Exception:
            credentials = None

    if credentials and credentials.valid:
        return credentials

    if (
        credentials
        and credentials.expired
        and credentials.refresh_token
    ):
        try:
            from google.auth.transport.requests import Request

            credentials.refresh(Request())

            save_token(credentials)

            return credentials

        except Exception:
            credentials = None

    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(
            "Google OAuth credentials were not found."
        )

    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        SCOPES
    )

    credentials = flow.run_local_server(
        port=0
    )

    save_token(credentials)

    return credentials


def save_token(credentials):
    ensure_app_data_dir()

    with open(
        TOKEN_FILE,
        "w",
        encoding="utf-8"
    ) as token_file:
        token_file.write(
            credentials.to_json()
        )


def get_youtube_service():
    credentials = authenticate()

    return build(
        "youtube",
        "v3",
        credentials=credentials
    )


def remove_token():
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()


def remove_credentials():
    if CREDENTIALS_FILE.exists():
        CREDENTIALS_FILE.unlink()


def reset_auth():
    remove_token()
    remove_credentials()