# database.py
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_DIR = os.environ.get("DATABASE_DIR", ".")
DATABASE_URL = f"sqlite:///{DB_DIR}/taskmanager.db"
# Create the SQLAlchemy engine
# connect_args={"check_same_thread": False} is crucial for SQLite
# It tells SQLite that multiple threads might access the database connection,
# which is common in web servers like Uvicorn.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# Create a SessionLocal class for database sessions
# autocommit=False ensures transactions are managed manually
# autoflush=False prevents immediate flushing of changes
# bind=engine links sessions to our database engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base class for our declarative models
# All SQLAlchemy models will inherit from this Base
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()