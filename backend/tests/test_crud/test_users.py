import pytest
from fastapi import HTTPException

from backend.crud.user import get_user
from backend.tests.conftests import db_session, test_art_data

@pytest.mark.asyncio
async def test_get_users(db_session, test_art_data):
    result = await get_user(db_session)
    result_with_exist_id = await get_user(db_session, 1)
    result_with_exist_email = await get_user(db_session, email='test_user1@mail.ru')
    with pytest.raises(HTTPException) as exc_info:
        await get_user(db_session, 3)
    with pytest.raises(HTTPException) as exc_info2:
        await get_user(db_session, email='test_user3@mail.ru')
    assert len(result) == 2
    assert result_with_exist_id.full_name == 'test_user'
    assert result_with_exist_email.email == 'test_user1@mail.ru'
    assert exc_info.value.status_code == 404
    assert exc_info2.value.status_code == 404