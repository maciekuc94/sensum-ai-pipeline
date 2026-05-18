"""OAuth 2.0 auth for YouTube channel account (token_youtube.json)."""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

_PROJECT_ROOT = Path(__file__).parent.parent
_CREDENTIALS_PATH = _PROJECT_ROOT / "credentials.json"
_TOKEN_PATH = _PROJECT_ROOT / "token_youtube.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
]


def get_youtube_credentials() -> Credentials:
    """Return valid credentials for the YouTube channel account.

    On first call: opens browser for user to sign in with their YouTube channel
    Google account. Saves token to token_youtube.json.
    On subsequent calls: loads and refreshes token silently.
    """
    creds = None
    if _TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(_TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not _CREDENTIALS_PATH.exists():
                raise FileNotFoundError(
                    f"credentials.json not found at {_CREDENTIALS_PATH}\n"
                    "Download it from Google Cloud Console → APIs & Services → Credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(_CREDENTIALS_PATH), SCOPES
            )
            creds = flow.run_local_server(port=0)
        _TOKEN_PATH.write_text(creds.to_json())

    return creds


def build_youtube(creds: Credentials):
    """Return a YouTube Data API v3 client."""
    return build("youtube", "v3", credentials=creds)


def build_analytics(creds: Credentials):
    """Return a YouTube Analytics API v2 client."""
    return build("youtubeAnalytics", "v2", credentials=creds)


def build_sheets(creds: Credentials):
    """Return a Google Sheets API v4 client."""
    return build("sheets", "v4", credentials=creds)
