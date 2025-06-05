from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import Depends

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@database:3306/waitkue"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL 
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
