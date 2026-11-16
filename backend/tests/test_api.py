import pytest
from app.models import User, Note, NoteUser


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


# Создание заметки.
def test_create_note_successfully(client, db_session):
    # Регистрация пользователя.
    register_response = client.post(
        "/auth/register",
        json={
            "display_name": "Atlant",
            "username": "atlant_notes",
            "password": "password123"
        }
    )
    assert register_response.status_code == 200

    # Авторизация пользователя.
    auth_response = client.post(
        "/auth/login",
        json={
            "username": "atlant_notes",
            "password": "password123"
        }
    )
    assert auth_response.status_code == 200

    access_token = auth_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Создание заметки.
    response = client.post(
        "/notes",
        json={
            "title": "Тестовая заметка",
            "content": "Содержимое заметки",
            "color": "#ffffff"
        },
        headers=headers
    )
    assert response.status_code == 200

    # Проверка ответа.
    response_data = response.json()
    assert response_data["title"] == "Тестовая заметка"
    assert response_data["content"] == "Содержимое заметки"
    assert response_data["color"] == "#ffffff"

    # Проверка записи в БД.
    user = db_session.query(User).filter(
        User.username == "atlant_notes"
    ).first()

    note = db_session.query(Note).filter(
        Note.title == "Тестовая заметка"
    ).first()

    assert note is not None
    assert note.owner_id == user.id
    assert note.content == "Содержимое заметки"
    assert note.color == "#ffffff"

    # Проверка связи заметки с владельцем.
    note_user = db_session.query(NoteUser).filter(
        NoteUser.note_id == note.id,
        NoteUser.user_id == user.id
    ).first()

    assert note_user is not None
    assert note_user.is_editor is False
    assert note_user.is_archived is False
    assert note_user.deleted_at is None

# Получение списка заметок пользователя.
def test_get_notes_successfully(client, db_session):
    # Регистрация пользователя.
    register_response = client.post(
        "/auth/register",
        json={
            "display_name": "Atlant",
            "username": "atlant_notes",
            "password": "password123"
        }
    )
    assert register_response.status_code == 200

    # Авторизация пользователя.
    auth_response = client.post(
        "/auth/login",
        json={
            "username": "atlant_notes",
            "password": "password123"
        }
    )
    assert auth_response.status_code == 200

    access_token = auth_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Создание двух заметок.
    for title, content in [
        ("Первая заметка", "Первое содержимое"),
        ("Вторая заметка", "Второе содержимое")
    ]:
        response = client.post(
            "/notes",
            json={
                "title": title,
                "content": content,
                "color": "#ffffff"
            },
            headers=headers
        )
        assert response.status_code == 200

    # Получение списка заметок.
    response = client.get("/notes", headers=headers)
    assert response.status_code == 200

    # Проверка ответа.
    response_data = response.json()
    assert len(response_data) == 2

    notes = {note["title"]: note for note in response_data}

    assert "Первая заметка" in notes
    assert "Вторая заметка" in notes
    assert notes["Первая заметка"]["content"] == "Первое содержимое"
    assert notes["Вторая заметка"]["content"] == "Второе содержимое"
    assert notes["Первая заметка"]["color"] == "#ffffff"
    assert notes["Вторая заметка"]["color"] == "#ffffff"

    # Проверка записей в БД.
    user = db_session.query(User).filter(
        User.username == "atlant_notes"
    ).first()

    assert user is not None

    user_notes = db_session.query(NoteUser).filter(
        NoteUser.user_id == user.id,
        NoteUser.deleted_at.is_(None),
        NoteUser.is_archived.is_(False)
    ).all()

    assert len(user_notes) == 2