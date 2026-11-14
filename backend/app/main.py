import os
from datetime import datetime, timezone, timedelta
import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import ExpiredSignatureError, InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models import User, Note, Tag
from schemas import UserRegister, UserResponse, UserLogin, TokenResponse, NoteCreate, NoteResponse, NoteUpdate, \
    TagResponse

load_dotenv(encoding="utf-8")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

app = FastAPI()
password_hash = PasswordHash.recommended()
security = HTTPBearer()

def create_access_token(user_id):
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(EXPIRE_MINUTES))
    token = jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return token

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Время действия токена истекло.")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Некорректный токен.")

    user_id = int(payload['sub'])
    current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user:
        raise HTTPException(status_code=401, detail="Пользователя с такими данными не найдено.")
    return current_user

@app.get("/")
def index():
    return {"message": "Записывай то, что не забудете вместе!"}

# NOTE ENDPOINTS.

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
def get_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(display_name=current_user.display_name, username=current_user.username)

# Создать заметку.
@app.post("/notes", response_model=NoteResponse)
def create_note(
        note_data: NoteCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    new_note = Note(
        owner_id=current_user.id,
        title=note_data.title,
        content=note_data.content,
        color=note_data.color
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return NoteResponse.model_validate(new_note)


# Получить список заметок пользователя.
@app.get("/notes", response_model=list[NoteResponse])
def get_notes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_notes = db.query(Note).filter(
        current_user.id == Note.owner_id,
        Note.deleted_at.is_(None),
        Note.is_archived.is_(False)
    ).all()
    return [NoteResponse.model_validate(user_note) for user_note in user_notes]

@app.get("/notes/archive", response_model=list[NoteResponse])
def get_archived_notes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_notes = db.query(Note).filter(
        current_user.id == Note.owner_id,
        Note.is_archived.is_(True),
        Note.deleted_at.is_(None)
    ).all()
    return [NoteResponse.model_validate(user_note) for user_note in user_notes]

@app.get("/notes/trash", response_model=list[NoteResponse])
def get_trashed_notes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_notes = db.query(Note).filter(
        Note.owner_id == current_user.id,
        Note.deleted_at.is_not(None)
    ).all()
    return [NoteResponse.model_validate(user_note) for user_note in user_notes]

# Сведения конкретной заметки пользователя.
@app.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_note = db.query(Note).filter(
        current_user.id == Note.owner_id,
        Note.id == note_id,
        Note.deleted_at.is_(None)
    ).first()
    if user_note is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена.")
    return NoteResponse.model_validate(user_note)

# Редактировать заметку.
@app.patch("/notes/{note_id}", response_model=NoteResponse)
def edit_note(note_id: int, note_data: NoteUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_note = db.query(Note).filter(
        current_user.id == Note.owner_id,
        Note.id == note_id,
        Note.deleted_at.is_(None),
    ).first()
    if user_note is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена.")
    changes = note_data.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="Полей для изменений не найдено.")
    for key, value in changes.items():
        setattr(user_note, key, value)
    db.commit()
    db.refresh(user_note)
    return NoteResponse.model_validate(user_note)


# Удалить заметку.
@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_note = db.query(Note).filter(
        note_id == Note.id,
        current_user.id == Note.owner_id,
        Note.deleted_at.is_(None)
    ).first()
    if user_note is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена.")
    user_note.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Восстановление заметки из корзины.
@app.patch("/notes/{note_id}/restore", response_model=NoteResponse)
def restore_the_note(note_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_note = db.query(Note).filter(
        note_id == Note.id,
        current_user.id == Note.owner_id,
        Note.deleted_at.is_not(None)
    ).first()
    if user_note is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена.")
    user_note.deleted_at = None
    db.commit()
    db.refresh(user_note)
    return NoteResponse.model_validate(user_note)

@app.delete("/notes/{note_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
def permanently_delete_note(note_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_note = db.query(Note).filter(
        note_id == Note.id,
        current_user.id == Note.owner_id,
        Note.deleted_at.is_not(None)
    ).first()
    if user_note is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена.")
    db.delete(user_note)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# TAGS ENDPOINTS.

@app.get("/tags", response_model=list[TagResponse])
def get_available_tags(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tags = db.query(Tag).filter(or_(current_user.id == Tag.user_id,Tag.default_tag.is_(True))).all()
    return [TagResponse.model_validate(tag) for tag in tags]