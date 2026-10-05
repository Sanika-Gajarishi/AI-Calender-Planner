from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User


class AuthService:

    def __init__(self, db: Session):
        self.db = db

    def register(
        self,
        email: str,
        password: str,
        name: str | None = None,
    ):

        existing_user = (
            self.db.query(User)
            .filter(
                User.email == email
            )
            .first()
        )

        if existing_user:
            raise ValueError(
                "User with this email already exists."
            )

        user = User(
            name=name or email.partition("@")[0],
            email=email,
            hashed_password=hash_password(
                password
            ),
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def login(
        self,
        email: str,
        password: str,
    ):

        user = (
            self.db.query(User)
            .filter(
                User.email == email
            )
            .first()
        )

        if not user:
            raise ValueError(
                "Invalid email or password."
            )

        if user.hashed_password is None:
            raise ValueError(
                "Invalid email or password."
            )

        if not verify_password(
            password,
            user.hashed_password,
        ):
            raise ValueError(
                "Invalid email or password."
            )

        return create_access_token(
            user.id
        )