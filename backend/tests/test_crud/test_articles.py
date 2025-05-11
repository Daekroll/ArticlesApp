import pytest
from fastapi import HTTPException

from backend.crud.articles import get_articles
from backend.tests.conftests import db_session, test_art_data

@pytest.mark.asyncio
async def test_get_articles(db_session, test_art_data):
    result = await get_articles(db_session)
    result_with_exist_id = await get_articles(db_session, 1)
    with pytest.raises(HTTPException) as exc_info:
        await get_articles(db_session, 3)
    assert len(result) == 2
    assert result[0].title == 'Test article with author'
    assert result[1].author_id is None
    assert result_with_exist_id.content == 'Content article 1'
    assert exc_info.value.status_code == 404

