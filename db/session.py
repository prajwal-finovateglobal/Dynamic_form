import os
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated, Generator
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from core.config import DATABASE_URL
from utils.logger import get_logger

logger = get_logger("db/session_logger")

# Load environment variables from .env file
load_dotenv()

# Create the database engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()

metadata = MetaData()
metadata.reflect(bind=engine)

# Test the database connection
try:
    with engine.connect() as connection:
        logger.info("Database connection successful")
except SQLAlchemyError as e:
    logger.error(f"Database connection failed: {e}")
    raise 