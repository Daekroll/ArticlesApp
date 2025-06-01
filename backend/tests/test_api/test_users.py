from api.v1.endpoints.users import router as users_router
from tests.conftests import auth_client, db_session, app, test_data
from db.session import get_db
from crud.user import get_user


async def test_read_users_by_base_user(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client(0)
    response = await client.get(f'{users_router.prefix}/users')
    response_data = response.json()

    assert response.status_code == 403
    assert response_data['detail'] == 'You don`t have permission'


async def test_read_users_by_staff(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client()
    response = await client.get(f'{users_router.prefix}/users')
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data) == 4
    assert response_data[0].get('email') == 'test_user@mail.ru'


async def test_profile(db_session, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client(0)
    response = await client.get(f'{users_router.prefix}/profile')
    response_data = response.json()

    assert response.status_code == 200
    assert response_data.get('email') == 'test_user@mail.ru'


async def test_update_user_by_staff(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client()
    old_user_status = await get_user(db_session, 3)
    assert old_user_status.email == 'test_user2@mail.ru'
    data = {'email':'123@mail.ru'}
    response = await client.patch(f'{users_router.prefix}/update/3',
                                  json=data,
                                  headers={'Content-Type':'application/json'})
    response_data = response.json()

    new_user_status = await get_user(db_session, 3)
    assert new_user_status.email == '123@mail.ru'
    assert response_data.get('message') == 'Update successfully'
    assert response.status_code == 200


async def test_update_self_by_user(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client(0)
    old_user_status = await get_user(db_session, 1)
    assert old_user_status.full_name == 'test_user'
    data = {'full_name':'Bob'}
    response = await client.patch(f'{users_router.prefix}/update/1',
                                  json=data,
                                  headers={'Content-Type':'application/json'})
    response_data = response.json()

    new_user_status = await get_user(db_session, 1)
    assert new_user_status.full_name == 'Bob'
    assert response_data.get('message') == 'Update successfully'
    assert response.status_code == 200

async def test_update_other_user_by_user(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client(0)
    old_user_status = await get_user(db_session, 2)
    assert old_user_status.full_name == 'test_user1'
    data = {'full_name':'Bob'}
    response = await client.patch(f'{users_router.prefix}/update/2',
                                  json=data,
                                  headers={'Content-Type':'application/json'})
    response_data = response.json()

    new_user_status = await get_user(db_session, 2)
    assert new_user_status.full_name == 'test_user1'
    assert response_data.get('detail') == 'You don`t have permission'
    assert response.status_code == 403


async def test_update_non_exist_user(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client()
    data = {'full_name':'Bob'}
    response = await client.patch(f'{users_router.prefix}/update/5',
                                  json=data,
                                  headers={'Content-Type':'application/json'})
    response_data = response.json()

    assert response_data.get('detail') == 'User not found'
    assert response.status_code == 404


async def test_delete_self_by_user(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client(0)
    old_count_user = await get_user(db_session)
    assert len(old_count_user) == 4
    response = await client.delete(f'{users_router.prefix}/delete/1')
    response_data = response.json()
    new_count_user = await get_user(db_session)
    assert len(new_count_user) == 3
    assert response_data.get('message') == 'User deleted'
    assert response.status_code == 200


async def test_delete_other_user_by_staff(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client()
    old_count_user = await get_user(db_session)
    assert len(old_count_user) == 4
    response = await client.delete(f'{users_router.prefix}/delete/1')
    response_data = response.json()
    new_count_user = await get_user(db_session)
    assert len(new_count_user) == 3
    assert response_data.get('message') == 'User deleted'
    assert response.status_code == 200


async def test_delete_non_exist_by_staff(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client()
    old_count_user = await get_user(db_session)
    assert len(old_count_user) == 4
    response = await client.delete(f'{users_router.prefix}/delete/6')
    response_data = response.json()
    new_count_user = await get_user(db_session)
    assert len(new_count_user) == 4
    assert response_data.get('detail') == 'User not found'
    assert response.status_code == 404


async def test_delete_other_user_by_user(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client(1)
    old_count_user = await get_user(db_session)
    assert len(old_count_user) == 4
    response = await client.delete(f'{users_router.prefix}/delete/3')
    response_data = response.json()
    new_count_user = await get_user(db_session)
    assert len(new_count_user) == 4
    assert response_data.get('detail') == 'You don`t have permission'
    assert response.status_code == 403