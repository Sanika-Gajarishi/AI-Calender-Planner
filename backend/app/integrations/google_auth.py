import os
from pathlib import Path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]



BACKEND_DIR = Path(__file__).resolve().parents[2]

CREDENTIALS_FILE = (
    BACKEND_DIR
    / "credentials"
    / "google_client_secret.json"
)

if not CREDENTIALS_FILE.exists():

    CREDENTIALS_FILE = (
        BACKEND_DIR
        / "credentials"
        / "google_client_secret.json.json"
    )


TOKEN_FILE = BACKEND_DIR / "token.json"


def get_google_credentials():

    credentials = None

    

    if TOKEN_FILE.exists():

        credentials = (
            Credentials.from_authorized_user_file(
                TOKEN_FILE,
                SCOPES,
            )
        )

    

    if credentials and credentials.valid:

        return credentials

   

    if (
        credentials
        and credentials.expired
        and credentials.refresh_token
    ):

        try:

            credentials.refresh(
                Request()
            )

            print(
                "Google Calendar token refreshed successfully."
            )

        except RefreshError:

            print(
                "Google Calendar token is expired "
                "or revoked."
            )

            print(
                "Starting Google OAuth authorization again..."
            )

            credentials = None



    if credentials is None:

        if not CREDENTIALS_FILE.exists():

            raise FileNotFoundError(
                f"Google OAuth client file not found: "
                f"{CREDENTIALS_FILE}"
            )

        flow = (
            InstalledAppFlow
            .from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES,
            )
        )

        credentials = flow.run_local_server(
            port=0
        )

        print(
            "Google Calendar authorization successful."
        )

    
    with open(
        TOKEN_FILE,
        "w",
    ) as token:

        token.write(
            credentials.to_json()
        )

    return credentials