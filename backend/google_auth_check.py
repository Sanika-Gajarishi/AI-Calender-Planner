from app.integrations.google_auth import (
    get_google_credentials,
)


credentials = get_google_credentials()

print("Google authentication successful.")
print(
    "Token valid:",
    credentials.valid,
)