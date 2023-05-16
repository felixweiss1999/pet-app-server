from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} #argument needed for sqlite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#this in itself is not a session yet, but every instance of SessionLocal will be

Base = declarative_base()
#will later inherit from this class to create each of the databse ORM models
