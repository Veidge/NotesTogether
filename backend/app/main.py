import os
from datetime import datetime, timezone, timedelta
import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from schemas import UserRegister, UserResponse, UserLogin, TokenResponse

load_dotenv(encoding="utf-8")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

app = FastAPI()
password_hash = PasswordHash.recommended()

def create_access_token(user_id):
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(EXPIRE_MINUTES))
    token = jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return token

@app.get("/")
def index():
    return {"message": "Записывай то, что не забудете вместе!"}

@app.post("/auth/register")
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    display_name = user.display_name
    username = user.username

    checking_user = db.query(User).filter(User.username == username).first()
    if checking_user:
        raise HTTPException(status_code=409, detail="Пользователь с таким именем уже существует.")
    hashed_password = password_hash.hash(user.password)
    new_user = User(display_name=display_name, username=username, password=hashed_password)
    db.add(new_user)
    db.commit()
    return UserResponse(display_name=display_name, username=username)


@app.post("/auth/login")
def authentification(user: UserLogin, db: Session = Depends(get_db)):
    username = user.username
    password = user.password

    checking_user = db.query(User).filter(User.username == username).first()
    if not checking_user or not password_hash.verify(password, checking_user.password):
        raise HTTPException(status_code=401, detail="Пользователя с такими данными не найдено.")
    token = create_access_token(checking_user.id)
    return TokenResponse(access_token=token, token_type="bearer")



@app.get("/auth/me")
def get_user_info(user_id):
    pass


@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    checked_user = db.query(User).filter(User.username == "veidge").first()
    if checked_user is not None:
        return checked_user.display_name
    return None