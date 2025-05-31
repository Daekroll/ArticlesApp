from async_asgi_testclient import TestClient

from backend.api.v1.endpoints.articles import router as articles_router
from backend.tests.conftests import auth_client, db_session, app, test_data
from backend.db.session import get_db
from backend.crud.articles import get_articles


async def test_get_article(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    response = await TestClient(app).get(f'{articles_router.prefix}/')
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data) == 2


async def test_get_one_article(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    response = await TestClient(app).get(f'{articles_router.prefix}/1')
    response_data = response.json()

    assert response.status_code == 200
    assert response_data.get('title') == 'Test article with author'


async def test_get_one_not_exist_article(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    response = await TestClient(app).get(f'{articles_router.prefix}/4')
    response_data = response.json()

    assert response.status_code == 404
    assert response_data.get('detail') == 'Article not found'


async def test_create_article_by_active_user(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client(0)
    data={
        'title':'New Article',
        'content':'bla bla bla'
    }
    old_article_count = await get_articles(db_session)
    assert len(old_article_count) == 2
    response = await client.post(f'{articles_router.prefix}/create',
                                json=data,
                                headers={'Content-Type':'application/json'})
    response_data = response.json()
    new_article_count = await get_articles(db_session)
    assert len(new_article_count) == 3
    assert response.status_code == 200
    assert response_data.get('message') == 'Article create'


async def test_create_article_by_not_active_user(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client(2)
    data={
        'title':'New Article',
        'content':'bla bla bla'
    }
    old_article_count = await get_articles(db_session)
    assert len(old_article_count) == 2
    response = await client.post(f'{articles_router.prefix}/create',
                                json=data,
                                headers={'Content-Type':'application/json'})
    response_data = response.json()
    new_article_count = await get_articles(db_session)
    assert len(new_article_count) == 2
    assert response.status_code == 403
    assert response_data.get('detail') == 'You need to confirm email'

async def test_create_article_by_not_user(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    data = {
        'title': 'New Article',
        'content': 'bla bla bla'
    }
    old_article_count = await get_articles(db_session)
    assert len(old_article_count) == 2
    response = await TestClient(app).post(f'{articles_router.prefix}/create',
                                 json=data,
                                 headers={'Content-Type': 'application/json'})
    response_data = response.json()
    new_article_count = await get_articles(db_session)
    assert len(new_article_count) == 2
    assert response.status_code == 401
    assert response_data.get('detail') == 'Not authenticated'


async def test_update_article_by_user(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client(0)
    data={
        'content':'bla bla bla'
    }
    old_article_count = await get_articles(db_session, 1)
    assert old_article_count.content == 'Content article 1'
    response = await client.patch(f'{articles_router.prefix}/update/1',
                                json=data,
                                headers={'Content-Type':'application/json'})
    response_data = response.json()
    new_article_count = await get_articles(db_session,1)
    assert new_article_count.content == 'bla bla bla'
    assert response.status_code == 200
    assert response_data.get('message') == 'Article updated'


async def test_update_other_article_by_user(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client(0)
    data={
        'content':'bla bla bla'
    }
    old_article_count = await get_articles(db_session, 2)
    assert old_article_count.content == 'Content article 2'
    response = await client.patch(f'{articles_router.prefix}/update/2',
                                json=data,
                                headers={'Content-Type':'application/json'})
    response_data = response.json()
    new_article_count = await get_articles(db_session,2)
    assert new_article_count.content == 'Content article 2'
    assert response.status_code == 403
    assert response_data.get('detail') == 'You don`t have permission'


async def test_update_other_article_by_staff(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client()
    data={
        'content':'bla bla bla'
    }
    old_article_count = await get_articles(db_session, 2)
    assert old_article_count.content == 'Content article 2'
    response = await client.patch(f'{articles_router.prefix}/update/2',
                                json=data,
                                headers={'Content-Type':'application/json'})
    response_data = response.json()
    new_article_count = await get_articles(db_session,2)
    assert new_article_count.content == 'bla bla bla'
    assert response.status_code == 200
    assert response_data.get('message') == 'Article updated'


async def test_update_not_exist_article_by_staff(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client()
    data={
        'content':'bla bla bla'
    }
    response = await client.patch(f'{articles_router.prefix}/update/9',
                                json=data,
                                headers={'Content-Type':'application/json'})
    response_data = response.json()
    assert response.status_code == 404
    assert response_data.get('detail') == 'Article not found'


async def test_delete_other_article_by_staff(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client()

    old_article_count = await get_articles(db_session)
    assert len(old_article_count) == 2
    response = await client.delete(f'{articles_router.prefix}/delete/1')
    response_data = response.json()
    new_article_count = await get_articles(db_session)
    assert len(new_article_count) == 1
    assert response.status_code == 200
    assert response_data.get('message') == 'Article deleted'


async def test_delete_other_article_by_user(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client(0)

    old_article_count = await get_articles(db_session)
    assert len(old_article_count) == 2
    response = await client.delete(f'{articles_router.prefix}/delete/2')
    response_data = response.json()
    new_article_count = await get_articles(db_session)
    assert len(new_article_count) == 2
    assert response.status_code == 403
    assert response_data.get('detail') == 'You don`t have permission'


async def test_delete_self_article_by_user(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client(0)

    old_article_count = await get_articles(db_session)
    assert len(old_article_count) == 2
    response = await client.delete(f'{articles_router.prefix}/delete/1')
    response_data = response.json()
    new_article_count = await get_articles(db_session)
    assert len(new_article_count) == 1
    assert response.status_code == 200
    assert response_data.get('message') == 'Article deleted'


async def test_delete_not_exist_article_by_staff(db_session, test_data, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session
    client = await auth_client()

    old_article_count = await get_articles(db_session)
    assert len(old_article_count) == 2
    response = await client.delete(f'{articles_router.prefix}/delete/9')
    response_data = response.json()
    new_article_count = await get_articles(db_session)
    assert len(new_article_count) == 2
    assert response.status_code == 404
    assert response_data.get('detail') == 'Article not found'