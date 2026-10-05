from sqlalchemy import inspect
from app.database.connection import engine

inspector = inspect(engine)

print("Database tables:")
for table in inspector.get_table_names():
    print("-", table)
