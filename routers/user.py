from fastapi_crudrouter import SQLAlchemyCRUDRouter as CRUDRouter
from models import User
from schemas import CreateUserSchema, UserSchema
from database import get_db
from .auth import get_password_hash
from sqlalchemy.orm import Session, joinedload
from fastapi import Depends
from typing import Optional, Dict

router = CRUDRouter(
    schema=UserSchema,
    create_schema=CreateUserSchema , 
    db_model=User,
    db=get_db
)

@router.post("")
async def signup_user(form_data: CreateUserSchema, db: Session = Depends(get_db)):
    
    form_data.password_hash = get_password_hash(form_data.password_hash)
    
    db_model: User = User(**form_data.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

@router.post("/clients")
async def client_users(db: Session = Depends(get_db)):
    return db.query(User).filter_by(role='client').all()

@router.put("")
async def update_profile(item_id: int, form_data: CreateUserSchema, db: Session = Depends(get_db)):
    
    user = db.query(User).get(item_id)
    
    if len(form_data.password_hash) > 7:
        form_data.password_hash = get_password_hash(form_data.password_hash)
    else:
        form_data.password_hash = user.password_hash
    
    db.query(User).filter_by(id=item_id)\
        .update(**form_data.dict())
    db.commit()
    db.refresh()
    
    return user