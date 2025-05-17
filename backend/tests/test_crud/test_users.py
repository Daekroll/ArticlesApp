import pytest
from fastapi import HTTPException

from backend.crud.user import get_user, create, read, update, delete
from backend.tests.conftests import db_session, test_data
from backend.schemas.user import UserCreate, UserUpdate


@pytest.mark.asyncio
async def test_get_users(db_session, test_data):
    result = await get_user(db_session)
    result_with_exist_id = await get_user(db_session, 1)
    with pytest.raises(HTTPException) as exc_info:
        await get_user(db_session, 5)
    assert len(result) == 4
    assert result_with_exist_id.full_name == 'test_user'
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_create_user(db_session, test_data):
    user = UserCreate(
        email='vavilonskiy99@mail.ru',
        password='Qwerty741',
        full_name='Ivan Ivanov',
    )
    users_before_create = await get_user(db_session)
    create_user = await create(user, db_session)
    users_after_create = await get_user(db_session)

    assert len(users_before_create) == 4
    assert len(users_after_create) == 5
    assert create_user.get('message') == 'Successfully registered'
    assert create_user.get('status') == 201


@pytest.mark.asyncio
async def test_create_user_with_exist_email(db_session, test_data):
    user = UserCreate(
        email='test_user@mail.ru',
        password='Qwerty741',
        full_name='Ivan Ivanov',
    )
    users_before_create = await get_user(db_session)
    with pytest.raises(HTTPException) as exc_info:
        await create(user, db_session)
    users_after_create = await get_user(db_session)

    assert len(users_before_create) == len(users_after_create) == 4
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == 'Email alredy registered'


@pytest.mark.asyncio
async def test_create_user(db_session, test_data):
    user = UserCreate(
        email='vavilonskiy99@mail.ru',
        password='Qwerty741',
        full_name='Ivan Ivanov',
    )
    users_before_create = await get_user(db_session)
    create_user = await create(user, db_session)
    users_after_create = await get_user(db_session)

    assert len(users_before_create) == 4
    assert len(users_after_create) == 5
    assert create_user.get('message') == 'Successfully registered'
    assert create_user.get('status') == 201


@pytest.mark.asyncio
async def test_read_user_list_by_staff(db_session, test_data):
    current_user = test_data.get('users')
    users_list = await read(current_user[3], db_session, user_list=True)

    assert len(users_list) == 4
    assert users_list[0].full_name == 'test_user'
    assert users_list[3].is_staff is True


@pytest.mark.asyncio
async def test_read_user_list_by_not_staff(db_session, test_data):
    current_user = test_data.get('users')
    with pytest.raises(HTTPException) as exc_info:
        await read(current_user[0], db_session, user_list=True)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == 'You don`t have permission'


@pytest.mark.asyncio
async def test_read_user_profile_by_staff(db_session, test_data):
    current_user = test_data.get('users')
    user = await read(current_user[3], db_session)

    assert user.full_name == 'test_admin_user'
    assert user.is_staff is True


@pytest.mark.asyncio
async def test_read_user_profile_by_not_staff(db_session, test_data):
    current_user = test_data.get('users')
    user = await read(current_user[0], db_session)

    assert user.full_name == 'test_user'
    assert user.is_staff is False


@pytest.mark.asyncio
async def test_update_other_user_by_staff(db_session, test_data):
    current_user = test_data.get('users')
    data = UserUpdate(
        full_name='John Doe'
    )
    users_before_update = await get_user(db_session)
    assert users_before_update[0].full_name == 'test_user'

    user = await update(1, current_user[3], db_session, data)
    users_after_update = await get_user(db_session)


    assert user.get('message') == 'Update successfully'
    assert user.get('status') == 200
    assert users_after_update[0].full_name == 'John Doe'

@pytest.mark.asyncio
async def test_self_update_by_user(db_session, test_data):
    current_user = test_data.get('users')
    data = UserUpdate(
        full_name='John Doe'
    )
    users_before_update = await get_user(db_session)
    assert users_before_update[1].full_name == 'test_user1'

    user = await update(2, current_user[1], db_session, data)
    users_after_update = await get_user(db_session)


    assert user.get('message') == 'Update successfully'
    assert user.get('status') == 200
    assert users_after_update[1].full_name == 'John Doe'

@pytest.mark.asyncio
async def test_update_other_user_by_not_staff(db_session, test_data):
    current_user = test_data.get('users')
    data = UserUpdate(
        full_name='John Doe'
    )
    users_before_update = await get_user(db_session)
    assert users_before_update[3].full_name == 'test_admin_user'
    with pytest.raises(HTTPException) as exc_info:
        await update(4, current_user[1], db_session, data)
    users_after_update = await get_user(db_session)


    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == 'You don`t have permission'
    assert users_after_update[3].full_name == 'test_admin_user'


@pytest.mark.asyncio
async def test_delete_other_user_by_staff(db_session, test_data):
    current_user = test_data.get('users')

    users_before_delete = await get_user(db_session)
    user_delete = await delete(1, current_user[3], db_session)
    users_after_delete = await get_user(db_session)


    assert len(users_before_delete) == 4
    assert len(users_after_delete) == 3
    assert user_delete.get('message') == 'User deleted'
    assert user_delete.get('status') == 200

@pytest.mark.asyncio
async def test_delete_other_user_by_not_staff(db_session, test_data):
    current_user = test_data.get('users')

    users_before_delete = await get_user(db_session)
    with pytest.raises(HTTPException) as exc_info:
        await delete(3, current_user[1], db_session)
    users_after_delete = await get_user(db_session)


    assert len(users_before_delete) == 4
    assert len(users_after_delete) == 4
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == 'You don`t have permission'


@pytest.mark.asyncio
async def test_self_delete__user(db_session, test_data):
    current_user = test_data.get('users')

    users_before_delete = await get_user(db_session)
    user_delete = await delete(1, current_user[0], db_session)
    users_after_delete = await get_user(db_session)


    assert len(users_before_delete) == 4
    assert len(users_after_delete) == 3
    assert user_delete.get('message') == 'User deleted'
    assert user_delete.get('status') == 200