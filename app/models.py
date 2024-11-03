from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
# from app.database import Base
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    role = Column(String)  # either "admin" or "user"
    password_hash = Column(String)

    tasks = relationship("Task", back_populates="assignee")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    priority = Column(String)
    due_date = Column(DateTime)
    status = Column(String, default="Pending")

    assignee = relationship("User", back_populates="tasks")
