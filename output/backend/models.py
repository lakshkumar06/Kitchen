"""
SQLAlchemy Models
Generated according to: FastAPI structure, SQLAlchemy models, CRUD endpoints
"""
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)

# Add your models here following the project requirements
