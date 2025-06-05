from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import Depends

SQLALCHEMY_DATABASE_URL = "postgresql://waitkue_user:nxVnolHVKnoZpt8Ge9R1LNKXm17tPBLp@dpg-d10nbjumcj7s73bsf6pg-a/waitkue"

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
