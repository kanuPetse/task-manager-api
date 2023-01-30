# API FOR USER CREATION, AUTHENTICATION AND AUTHORIZATION
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from database import db_session
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

import models
import sys
sys.path.append("..")

# DATABASE


def db_con():
    try:
        db = db_session()
        yield db
    finally:
        db.close()


# AUTHENTICATION
crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_user(plain_pass: str, hashed_pass: str):
    return crypt_context.verify(secret=plain_pass, hash=hashed_pass)


# AUTHORIZATION
SECRET = "1C1CHBF_enZA1034ZA1034&oq=pa&aqs=chrome.0.69i59j69i57j69i59l2j0i271j69i60l2j69i61.1787j0j1"
ALGORITHM = "HS256"


def create_token(username: str, user_id: str, exp: datetime = None):
    payload = {
        "sub": username,
        "id": user_id
    }

    if exp:
        payload.update({"exp": exp})
    else:
        payload.update({"exp": datetime.utcnow()+timedelta(minutes=15)})

    return jwt.encode(claims=payload, key=SECRET, algorithm=ALGORITHM)

# TEMPLATES


class UserRec(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    plain_password: str


# API
router = APIRouter()


@router.post("/create/user")
async def create_user(user_rec: UserRec, db: Session = Depends(dependency=db_con)):
    try:
        new_user = models.User()
        new_user.username = user_rec.username
        new_user.email = user_rec.email
        new_user.first_name = user_rec.first_name
        new_user.last_name = user_rec.last_name
        new_user.hashed_password = crypt_context.encrypt(
            user_rec.plain_password)
        db.add(instance=new_user)
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request.")
    return {
        "status_code": status.HTTP_201_CREATED,
        "message": "User created."
    }


@router.post("/login")
async def login(login_form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(dependency=db_con)):
    username = login_form.username
    password = login_form.password
    # Check user input
    if username is None or password is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Enter Username and Password.")
    # Verify user password
    try:
        cur_user: models.User = db.query(models.User).filter(
            models.User.username == username).first()
        if verify_user(plain_pass=password, hashed_pass=cur_user.hashed_password):
            token = create_token(cur_user.username, cur_user.id)
            return {
                "status_code": 200,
                "message": token
            }
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Username or Password is incorrect.")
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Username or Password is incorrect.")
