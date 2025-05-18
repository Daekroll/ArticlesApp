from backend.api.v1.endpoints.auth import router as auth_router
from backend.tests.conftests import client, db_session, app
from backend.db.session import get_db


async def test_register_success(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    test_user = {
        "email": "vavilonskiy99@mail.ru",
        "password":"Qwerty741",
        "full_name": "Igor Admin"
    }
    async with client as c:
        response = await c.post(f'{auth_router.prefix}/register', json=test_user)

        response_data = response.json()

        assert response.status_code == 200
        assert response_data["message"] == "Successfully registered"
        assert response_data["status"] == 201
