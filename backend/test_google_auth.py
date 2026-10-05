from app.integrations.google_auth import get_google_credentials


def main():

    print(
        "Testing Google Calendar authentication..."
    )

    credentials = get_google_credentials()

    print(
        "Google authentication successful."
    )

    print(
        "Credentials valid:",
        credentials.valid,
    )

    print(
        "Token file created successfully."
    )


if __name__ == "__main__":
    main()