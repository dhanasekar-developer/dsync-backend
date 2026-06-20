from typing import Annotated
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings
from fastapi import Depends

engine = create_engine(settings.DATABASE_URL)

session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

def get_db():
    db = session()

    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]