from app.database.connection import engine


def test_database_connection():
    with engine.connect() as connection:
        print("Database connection successful!")