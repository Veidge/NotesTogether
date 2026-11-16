import pytest
from app.models import User


# Создание пользователя с сохраненением его данных.
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

# Регистрация пользователя повторно.
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

# Авторизация пользователя с возвращением токена.
def test_login_user_successfully(client):
    # Новый пользователь.
    register_response = client.post(
        "/auth/register",
        json={
            "display_name": "ГигаЧаД",
            "username": "giga_user_pro",
            "password": "ybnhgVv-12"
        }
    )
    assert register_response.status_code == 200

    # Авторизация по созданному пользователю.
    auth_response = client.post(
        "/auth/login",
        json={
            "username": "giga_user_pro",
            "password": "ybnhgVv-12"
        }
    )
    assert auth_response.status_code == 200

    # Получение структуры ответа и проверка её корректности.
    response_data = auth_response.json()
    assert "access_token" in response_data
    assert "token_type" in response_data
    assert response_data["token_type"] == "bearer"
    assert response_data["access_token"] != ""

# Авторизация пользователя с неверным паролем.
def test_login_user_wrong_password_unsuccessfully(client):
    # Новый пользователь.
    register_response = client.post(
        "/auth/register",
        json={
            "display_name": "ГигаЧаД",
            "username": "giga_user_pro",
            "password": "ybnhgVv-12"
        }
    )
    assert register_response.status_code == 200

    # Авторизация по созданному пользователю (ошибочный пароль).
    auth_response = client.post(
        "/auth/login",
        json={
            "username": "giga_user_pro",
            "password": "ybnhgVv_12"
        }
    )
    assert auth_response.status_code == 401
    assert auth_response.json()['detail'] == "Пользователя с такими данными не найдено."