import pytest
from pydantic import ValidationError
from schemas import UserRegister


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