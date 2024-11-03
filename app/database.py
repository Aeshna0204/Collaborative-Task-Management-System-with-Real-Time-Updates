from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from app.models import Base 

# Replace with your actual PostgreSQL connection details
DATABASE_URL = "postgresql://postgres:aesh123*@localhost:5432/task_management_db"
# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")

# Create the engine for PostgreSQLs
engine = create_engine(DATABASE_URL)

# SessionLocal provides a transactional scope to database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
# Base = declarative_base()
Base.metadata.create_all(bind=engine)
# Dependency to provide a database session in route functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
