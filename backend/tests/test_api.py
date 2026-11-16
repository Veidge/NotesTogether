import pytest
from app.models import User


def test_register_user_successfully(client, db_session):
    response = client.post(
        "/auth/register",
        json={
            "display_name": "Atlant",
            "username": "atlant_test",
            "password": "password123"
        }
    )
    assert response.status_code == 200 # успешно доставлено.
    response_data = response.json()

    assert response_data["display_name"] == "Atlant"
    assert response_data["username"] == "atlant_test"

    user = db_session.query(User).filter(
        User.username == "atlant_test"
    ).first()

    assert user is not None
    assert user.display_name == "Atlant"
    assert user.password != "password123" # пароль в виде хэша.

def test_register_user_again_unsuccessfully(client, db_session):
    response = client.post(
        "/auth/register",
        json={
            "display_name": "Atlant",
            "username": "atlant_test",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    # Дублирование существующего пользователя - 409 код. (Уже существует запись)
    new_response = client.post(
        "/auth/register",
        json={
            "display_name": "Atlant",
            "username": "atlant_test",
            "password": "password123"
        }
    )
    assert new_response.status_code == 409
    assert new_response.json()["detail"] == "Пользователь с таким именем уже существует."

    # Создался 1 пользователь из 2.
    users_count = db_session.query(User).filter(
        User.username == "atlant_test"
    ).count()
    assert users_count == 1

    # Создался именно тот пользователь.
    user = db_session.query(User).filter(
        User.username == "atlant_test"
    ).first()
    assert user is not None
    assert user.display_name == "Atlant"
    assert user.password != "password123"
