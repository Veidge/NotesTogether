import pytest
from pydantic import ValidationError
from schemas import UserRegister, NoteCreate


def test_user_register_rejects_blank_display_name():
    with pytest.raises(ValidationError):
        UserRegister(
            display_name="   ",
            username="testuser",
            password="password123"
        )

def test_user_register_rejects_short_password():
    with pytest.raises(ValidationError):
        UserRegister(
            display_name="Atlant",
            username="atlant_tay",
            password="123"
        )

def test_user_register_accepts_valid_data():
    user = UserRegister(
        display_name="Atlant",
        username="atlant_tay",
        password="short121123"
    )
    assert user.username == "atlant_tay"

def test_note_create_rejects_blank_title():
    with pytest.raises(ValidationError):
        NoteCreate(
            title="   ",
            content="Заметка",
            color="white"
        )

def test_note_create_rejects_long_title():
    with pytest.raises(ValidationError):
        NoteCreate(
            title="1" * 51,
            content="Заметка",
            color="white"
        )

def test_note_create_accepts_empty_content():
    note = NoteCreate(
        title="Заметка",
        content="",
        color="white"
    )
    assert note.title == "Заметка"