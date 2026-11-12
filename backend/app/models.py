from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    display_name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    note_user = relationship("NoteUser", back_populates="user", cascade="all")

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    default_tag = Column(Boolean, nullable=False, default=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    note_tag = relationship("NoteTag", back_populates="tag", cascade="all")

class Note(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False, default="")
    color = Column(String, nullable=False, default="#c5bdb1")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    is_archived = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)
    note_tag = relationship("NoteTag", back_populates="note", cascade="all, delete-orphan")
    note_user = relationship("NoteUser", back_populates="note", cascade="all, delete-orphan")

class NoteTag(Base):
    __tablename__ = 'note_tags'
    note_id = Column(Integer, ForeignKey('notes.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
    note = relationship("Note", back_populates="note_tag")
    tag = relationship("Tag", back_populates="note_tag")

class NoteUser(Base):
    __tablename__ = 'note_users'
    note_id = Column(Integer, ForeignKey('notes.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    is_editor = Column(Boolean, nullable=False, default=False)
    user = relationship("User", back_populates="note_user")
    note = relationship("Note", back_populates="note_user")