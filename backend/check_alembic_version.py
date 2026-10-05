from sqlalchemy import text
from app.database.connection import engine

with engine.connect() as conn:
    result = conn.execute(
        text("SELECT version_num FROM alembic_version")
    )
    rows = result.fetchall()

    print("Alembic versions:")
    for row in rows:
        print(row[0])
