from email.headerregistry import ContentTypeHeader

from async_asgi_testclient import TestClient
from prompt_toolkit import Application

from api.v1.endpoints.auth import router as auth_router
from tests.conftests import client, db_session, app, test_data
from db.session import get_db
from core.security import generate_timestamp_link
from core.settings import HOST, PORT


# async def test_register_success(db_session):
#     app.dependency_overrides[get_db] = lambda: db_session
#     test_user = {
#         "email": "vavilonskiy99@mail.ru",
#         "password":"Qwerty741",
#         "full_name": "Igor Admin"
#     }
#     async with TestClient(app) as c:
#         response = await c.post(f'{auth_router.prefix}/register', json=test_user)
#
#         response_data = response.json()
#
#         assert response.status_code == 200
#         assert response_data["message"] == "Successfully registered"
#         assert response_data["status"] == 201


async def test_activate_profile(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    full_link = test_data.get('full_link')
    confirmation_url = f'{auth_router.prefix}/reg-confirm/{full_link}'
    current_users = test_data.get('users')
    async with TestClient(app) as c:
        response = await c.get(confirmation_url)
        response_data = response.json()

        assert response.status_code == 200
        assert response_data["message"] == "User activate!"
        assert current_users[3].is_active == True
        assert current_users[3].activate_link is None

async def test_activate_profile_with_expired_token(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    full_link = test_data.get('full_link')
    confirmation_url = f'{auth_router.prefix}/reg-confirm/{full_link[:-1]}0'

    async with TestClient(app) as c:
        response = await c.get(confirmation_url)
        response_data = response.json()

        assert response.status_code == 400
        assert response_data.get('detail') == 'Token expired'


async def test_activate_profile_with_non_exists_token(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    full_link = test_data.get('full_link')
    confirmation_url = f'{auth_router.prefix}/reg-confirm/123_123_1'

    async with TestClient(app) as c:
        response = await c.get(confirmation_url)
        response_data = response.json()

        assert response.status_code == 404
        assert response_data.get('detail') == 'Confirm token invalid'


async def test_login_success(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    async with TestClient(app) as c:
        response = await c.post(f'{auth_router.prefix}/login',
                                headers={"Content-Type": "application/x-www-form-urlencoded"},
                                form={"username":"test_user@mail.ru", "password":"Qwerty147"}
                               )


        response_data = response.json()

        assert response.status_code == 200
        assert 'access_token' in response_data
        assert response_data['token_type'] == 'bearer'


async def test_login_with_user_non_exist(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    async with TestClient(app) as c:
        response = await c.post(f'{auth_router.prefix}/login',
                                headers={"Content-Type": "application/x-www-form-urlencoded"},
                                form={"username":"test_user9@mail.ru", "password":"Qwerty147"}
                               )


        response_data = response.json()

        assert response.status_code == 401
        assert response_data['detail'] == 'User does not exist'


async def test_login_with_not_correct_password(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    async with TestClient(app) as c:
        response = await c.post(f'{auth_router.prefix}/login',
                                headers={"Content-Type": "application/x-www-form-urlencoded"},
                                form={"username":"test_user@mail.ru", "password":"Qwerty741"}
                               )


        response_data = response.json()

        assert response.status_code == 401
        assert response_data['detail'] == 'Incorrect email or password'


async def test_logout_success(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    async with TestClient(app) as c:
        response = await c.post(f'{auth_router.prefix}/login',
                                headers={"Content-Type": "application/x-www-form-urlencoded"},
                                form={"username":"test_user@mail.ru", "password":"Qwerty147"}
                               )
        response_data = response.json()
        token = response_data['access_token']
        response = await c.post(f'{auth_router.prefix}/logout',
                                headers={"Authorization": f"Bearer {token}"}
                                )
        response_data = response.json()
        assert response.status_code == 200
        assert response_data.get('message') == 'Successful logged out'

async def test_get_link(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    user = test_data.get('users')[2]

    async with TestClient(app) as client:
        response = await client.post(
            f'{auth_router.prefix}/login',
            form={'username': user.email, 'password': 'Qwerty147'},
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )
        token = response.json().get('access_token')

        response = await client.get(
            f'{auth_router.prefix}/get_link',
            headers={'Authorization': f'Bearer {token}'}
        )

        data = response.json()

        assert response.status_code == 200
        assert data.get('message') == 'link was sent'