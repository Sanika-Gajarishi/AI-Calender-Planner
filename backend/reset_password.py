from getpass import getpass

from app.core.security import hash_password
from app.database.connection import SessionLocal
from app.models.user import User


def main():

    email = input("Enter email: ").strip()

    new_password = getpass(
        "Enter new password: "
    )

    confirm_password = getpass(
        "Confirm new password: "
    )

    if new_password != confirm_password:
        print("Passwords do not match.")
        return

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.email == email
            )
            .first()
        )

        if user is None:
            print(
                "No user found with this email."
            )
            return

        user.hashed_password = hash_password(
            new_password
        )

        db.commit()

        print(
            "Password updated successfully."
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()