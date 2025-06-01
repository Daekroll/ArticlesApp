import pytest
from fastapi import HTTPException

from crud.comments import create, read, delete
from tests.conftests import db_session, test_data
from schemas.comment import CommentCreate


@pytest.mark.asyncio
async def test_create_comment(db_session, test_data):
    comment = CommentCreate(
            content='Comment 1',
            article_id=1
        )
    user = test_data.get('users')[0]
    comments_before_create = await read(comment.article_id, db_session)
    create_comment = await create(user, comment, db_session)
    comments_after_create = await read(comment.article_id, db_session)

    assert len(comments_before_create) == 2
    assert len(comments_after_create) == 3
    assert create_comment.get('message') == 'Comment successfully added'
    assert create_comment.get('status') == 201

@pytest.mark.asyncio
async def test_create_comment_by_not_active(db_session, test_data):
    comment = CommentCreate(
            content='Comment 1',
            article_id=1
        )
    user = test_data.get('users')[2]
    comments_before_create = await read(comment.article_id, db_session)
    with pytest.raises(HTTPException) as exc_info:
        await create(user, comment, db_session)
    comments_after_create = await read(comment.article_id, db_session)

    assert len(comments_before_create) == 2
    assert len(comments_after_create) == 2
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == 'You need to confirm email'


@pytest.mark.asyncio
async def test_read_comment(db_session, test_data):
    comments = await read(1, db_session)

    assert len(comments) == 2
    assert comments[0].content == 'Comment 1'
    assert comments[1].author_name == 'test_user1'


@pytest.mark.asyncio
async def test_delete_self_comment(db_session, test_data):

    user = test_data.get('users')[0]
    comments_before_delete = await read(1, db_session)
    delete_comment = await delete(1, user, db_session)
    comments_after_delete = await read(1, db_session)

    assert len(comments_before_delete) == 2
    assert len(comments_after_delete) == 1
    assert delete_comment.get('message') == 'Comment deleted'
    assert delete_comment.get('status') == 200

@pytest.mark.asyncio
async def test_delete_other_comment_by_staff(db_session, test_data):

    user = test_data.get('users')[3]
    comments_before_delete = await read(1, db_session)
    delete_comment = await delete(1, user, db_session)
    comments_after_delete = await read(1, db_session)

    assert len(comments_before_delete) == 2
    assert len(comments_after_delete) == 1
    assert delete_comment.get('message') == 'Comment deleted'
    assert delete_comment.get('status') == 200

@pytest.mark.asyncio
async def test_delete_other_comment_by_not_staff(db_session, test_data):

    user = test_data.get('users')[0]
    comments_before_delete = await read(2, db_session)
    with pytest.raises(HTTPException) as exc_info:
        await delete(3, user, db_session)
    comments_after_delete = await read(2, db_session)

    assert len(comments_before_delete) == 1
    assert len(comments_after_delete) == 1
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == 'You don`t have permission'