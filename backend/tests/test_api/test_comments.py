from async_asgi_testclient import TestClient

from api.v1.endpoints.comments import router as comments_router
from tests.conftests import auth_client, db_session, app, test_data
from db.session import get_db
from crud.comments import read


async def test_get_comments(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    response = await TestClient(app).get(f'{comments_router.prefix}/1')
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data) == 2


async def test_get_comments_by_not_exist_article(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    response = await TestClient(app).get(f'{comments_router.prefix}/3')
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data) == 0


async def test_create_comments_by_active_user(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client(0)
    data={
        'content':'content',
        'article_id':1,
    }
    old_comment_count = await read(1, db_session)
    assert len(old_comment_count) == 2
    response = await client.post(f'{comments_router.prefix}/create',
                                json=data,
                                headers={'Content-Type':'application/json'})
    response_data = response.json()
    new_comment_count = await read(1, db_session)
    assert len(new_comment_count) == 3
    assert response.status_code == 200
    assert response_data.get('message') == 'Comment successfully added'


async def test_create_comments_by_not_active_user(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client(2)
    data={
        'content':'content',
        'article_id':1,
    }
    old_comment_count = await read(1, db_session)
    assert len(old_comment_count) == 2
    response = await client.post(f'{comments_router.prefix}/create',
                                json=data,
                                headers={'Content-Type':'application/json'})
    response_data = response.json()
    new_comment_count = await read(1, db_session)
    assert len(new_comment_count) == 2
    assert response.status_code == 403
    assert response_data.get('detail') == 'You need to confirm email'


async def test_create_comments_by_not_user(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    data={
        'content':'content',
        'article_id':1,
    }
    old_comment_count = await read(1, db_session)
    assert len(old_comment_count) == 2
    response = await TestClient(app).post(f'{comments_router.prefix}/create',
                                json=data,
                                headers={'Content-Type':'application/json'})
    response_data = response.json()
    new_comment_count = await read(1, db_session)
    assert len(new_comment_count) == 2
    assert response.status_code == 401
    assert response_data.get('detail') == 'Not authenticated'


async def test_delete_comments_by_user(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client(0)

    old_comment_count = await read(1, db_session)
    assert len(old_comment_count) == 2
    response = await client.delete(f'{comments_router.prefix}/delete/1')
    response_data = response.json()
    new_comment_count = await read(1, db_session)
    assert len(new_comment_count) == 1
    assert response.status_code == 200
    assert response_data.get('message') == 'Comment deleted'


async def test_delete_comments_by_staff(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client()

    old_comment_count = await read(1, db_session)
    assert len(old_comment_count) == 2
    response = await client.delete(f'{comments_router.prefix}/delete/1')
    response_data = response.json()
    new_comment_count = await read(1, db_session)
    assert len(new_comment_count) == 1
    assert response.status_code == 200
    assert response_data.get('message') == 'Comment deleted'


async def test_delete_other_comments_by_user(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client(0)

    old_comment_count = await read(1, db_session)
    assert len(old_comment_count) == 2
    response = await client.delete(f'{comments_router.prefix}/delete/2')
    response_data = response.json()
    new_comment_count = await read(1, db_session)
    assert len(new_comment_count) == 2
    assert response.status_code == 403
    assert response_data.get('detail') == 'You don`t have permission'