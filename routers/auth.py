from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import jwt
from fastapi import Depends, APIRouter, HTTPException, Security, status, Response
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError

from database import get_db
from sqlalchemy.orm import Session
from models import User, Queue
from schemas import UserSchema, CreateUserSchema, SignupSchema

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "62a7334109bbc3756da22aa9e373f0e3c12c37e3f40fc117fb2c25649851a824"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300




class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserSchema


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list[str] = []


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"me": "Read information about the current user.", "items": "Read items."},
)

router = APIRouter(tags=["Auth"])


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    return db.query(User).filter_by(username=username).first()


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: Annotated[UserSchema, Security(get_current_user, scopes=["me"])],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.post("/signup")
async def signup_for_login(form_data: SignupSchema, db: Session = Depends(get_db)):
    
    emailArr = form_data.email.split("@")
    
    userData = CreateUserSchema(
        email=form_data.email,
        password_hash=get_password_hash(form_data.password),
        role="client",
        username=emailArr[0]
    )
    
    db_model: User = User(**userData.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> Token:
    print(form_data.scopes)
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer", user=user)


@router.get("/users/me/", response_model=UserSchema)
async def read_users_me(
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
):
    return current_user

@router.get("/status/")
async def read_system_status(current_user: Annotated[UserSchema, Depends(get_current_user)]):
    return {"status": "ok"}

@router.patch("/user/activate_tickets")
async def ractivate_tickets(current_user: Annotated[UserSchema, Depends(get_current_user)], db: Session = Depends(get_db)):
    
    db.query(Queue).filter(
        Queue.date == datetime.now().date(),
        Queue.time > datetime.now().time() ,
        Queue.step == 0,
        Queue.client_id == current_user.profile.id,
    ).update({
        Queue.step: 1
    })
    
    db.commit()
    db.refresh()
    
    raise HTTPException(200, "Tickets Activated")