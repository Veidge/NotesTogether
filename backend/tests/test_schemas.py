import pytest
from pydantic import ValidationError
from schemas import UserRegister, NoteCreate, NoteUpdate


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

def test_note_update_rejects_null_title():
    with pytest.raises(ValidationError):
        NoteUpdate(
            title=None,
            content="Заметка",
            color="white"
        )

def test_note_update_accepts_missing_title():
    new_note = NoteUpdate(
        content="Заметка",
        color="white"
    )
    assert new_note.title is None

def test_note_update_rejects_null_content():
    with pytest.raises(ValidationError):
        NoteUpdate(
            title="Заметка",
            content=None,
            color="white"
        )

def test_note_update_accepts_missing_content():
    new_note = NoteUpdate(
        title="Заметка",
        color="white"
    )
    assert new_note.content is None

def test_note_update_rejects_null_color():
    with pytest.raises(ValidationError):
        NoteUpdate(
            title="Заметка",
            content="Запомнить.",
            color=None
        )

def test_note_update_accepts_missing_color():
    new_note = NoteUpdate(
        title="Заметка",
        content="Запомнить."
    )
    assert new_note.color is None

def test_note_update_accepts_empty_data():
    new_note = NoteUpdate()
    assert new_note.title is None
    assert new_note.content is None
    assert new_note.color is None