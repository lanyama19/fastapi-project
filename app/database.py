from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import psycopg
from psycopg.rows import dict_row
import time
from .config import settings


# Normalize host for Windows where 'localhost' may misresolve
_host = settings.database_hostname.strip() if isinstance(settings.database_hostname, str) else "127.0.0.1"
if _host.lower() == "localhost":
    _host = "127.0.0.1"

# Synchronous (v1) database setup
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg://{settings.database_username}:{settings.database_password}@"
    f"{_host}:{settings.database_port}/{settings.database_name}"
)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Asynchronous (v2) database setup
ASYNC_SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.database_username}:{settings.database_password}@"
    f"{_host}:{settings.database_port}/{settings.database_name}"
)
async_engine = create_async_engine(
    ASYNC_SQLALCHEMY_DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
    pool_recycle=1800,
)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine)

Base = declarative_base()


# Dependency for synchronous (v1) sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency for asynchronous (v2) sessions
async def get_async_db():
    async with AsyncSessionLocal() as db:
        yield db


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
