# models.py
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base # Import Base from our database.py

class User(Base):
    # Define the table name in the database
    __tablename__ = 'users'
    # Define columns for the 'users' table
    id = Column(Integer, primary_key=True, index=True) # Primary key, auto-incrementing, indexed for fast lookups
    username = Column(String, unique=True) # Unique username
    password = Column(String) # Hashed password
    
    tasks = relationship("Task", back_populates="owner")

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="tasks")