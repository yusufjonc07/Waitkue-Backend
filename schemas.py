from datetime import time, date
from pydantic import BaseModel, validator, Field
from typing import Optional
from enum import Enum
from models import User
from fastapi import HTTPException

from database import get_db

class UserRoles(str, Enum):
    admin='admin'
    client='client'
    service_admin='service_admin'

class Genders(str, Enum):
    male='male'
    female='female'

class CreateServiceSchema(BaseModel):
    name: str
    description: str
    available_days: str
    room: int
    avg_minute: int
    from_time: time
    to_time: time
    image_url: str
    
class ServiceSchema(CreateServiceSchema):
    id: int
    class Config:
        orm_mode = True
class SignupSchema(BaseModel):
    email: str
    password: str
    @validator('email')
    def unique_name(cls: BaseModel, v: str) -> str:
        db = next(get_db())
        users = db.query(User).all()
        db.commit()
        if str(v) in set(map(lambda u: u.email, users)):
            raise HTTPException(status_code=400, detail='Email was registered before')
        return v
   
class CreateUserSchema(BaseModel):
    email: str
    role: UserRoles
    username: str = Field(min_length=5)
    password_hash: Optional[str] = Field(min_length=8, default='')
    

    @validator('username')
    def unique_name(cls: BaseModel, v: str) -> str:
        db = next(get_db())
        users = db.query(User).all()
        db.commit()
        if str(v) in set(map(lambda u: u.username, users)):
            raise HTTPException(status_code=400, detail='Login allaqachon foydalanilgan')
        return v

 
class CreateClientSchema(BaseModel):
    firstname: str
    surename: str
    middlename: str
    gender: Genders
    user_id: int
    
class ClientSchema(CreateClientSchema):
    id: int
    created_at: date
    fullname: str
    class Config:
        orm_mode = True

        
class CreateQueueSchema(BaseModel):
    service_id: int
    client_id: int
    time: time
    date: date 
    comment:str
    number: int


class UserSchema(BaseModel):
    id: int
    email: str
    role: UserRoles
    username: str = Field(min_length=5)
    disabled: bool
    profile: Optional[ClientSchema] = None
    class Config:
        orm_mode = True

class QueueSchema(CreateQueueSchema):
    id: int
    step: int
    in_room: bool
    created_at: date
    service: ServiceSchema
    client: UserSchema
    
    class Config:
        orm_mode = True
        
class Waitlist(BaseModel):
    queue_id: int
    number: int
    time: time
    status: int
    service: str
    
    class Config:
        orm_mode = True
        
class ReportYearlyChart(BaseModel):
    tickets: int
    month: str