from fastapi import FastAPI, Depends, HTTPException
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from schemas import UserRegister, UserResponse

app = FastAPI()

password_hash = PasswordHash.recommended()

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
def authentification():
    pass

@app.get("/auth/me")
def get_user_info(user_id):
    pass


@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    checked_user = db.query(User).filter(User.username == "veidge").first()
    if checked_user is not None:
        return checked_user.display_name
    return None