from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg
from psycopg.rows import dict_row
import time
from .config import settings


# Normalize host for Windows where 'localhost' may misresolve
_host = settings.database_hostname.strip() if isinstance(settings.database_hostname, str) else "127.0.0.1"
if _host.lower() == "localhost":
    _host = "127.0.0.1"

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg://{settings.database_username}:{settings.database_password}@"
    f"{_host}:{settings.database_port}/{settings.database_name}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# # Run native sql query using psycopg
# while True:
#     try:
#         conn = psycopg.connect(host = 'localhost', dbname = 'fastapi', row_factory=dict_row,
#                                user = 'postgres', password = '123', port = '5432')
#         cur = conn.cursor()
#         print("Database connection was succesful!")
#         break
#     except Exception as error:
#         print("connecting to database failed")
#         print("Error: ", error)
#         time.sleep(3)
