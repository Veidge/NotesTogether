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