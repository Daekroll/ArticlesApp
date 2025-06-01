import pytest
from fastapi import HTTPException

from crud.articles import get_articles, read, update, delete, create
from tests.conftests import db_session, test_data
from schemas.article import ArticleUpdate, ArticleCreate


@pytest.mark.asyncio
async def test_get_articles(db_session, test_data):
    result = await get_articles(db_session)
    result_with_exist_id = await get_articles(db_session, 1)
    with pytest.raises(HTTPException) as exc_info:
        await get_articles(db_session, 3)
    assert len(result) == 2
    assert result[0].title == 'Test article with author'
    assert result[1].author_id is None
    assert result_with_exist_id.content == 'Content article 1'
    assert exc_info.value.status_code == 404

@pytest.mark.asyncio
async def test_create_articles(db_session, test_data):
    current_user = test_data.get('users')
    article = ArticleCreate(
        title='Title for new article',
        content='Content for new article'
    )
    articles_before_create= await read(db_session)
    articles = await create(current_user[0], article, db_session)
    articles_after_create = await read(db_session)

    assert articles.get('message') == 'Article create'
    assert articles.get('status') == 201
    assert len(articles_before_create) == 2
    assert len(articles_after_create) == 3
    assert articles_after_create[2].title == 'Title for new article'
    assert articles_after_create[2].content == 'Content for new article...'

@pytest.mark.asyncio
async def test_create_articles_by_not_active_user(db_session, test_data):
    current_user = test_data.get('users')
    article = ArticleCreate(
        title='Title for new article',
        content='Content for new article'
    )
    articles_before_create = await read(db_session)
    with pytest.raises(HTTPException) as exc_info:
        await create(current_user[2], article, db_session)
    articles_after_create = await read(db_session)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == 'You need to confirm email'
    assert len(articles_before_create) == 2
    assert len(articles_after_create) == 2



@pytest.mark.asyncio
async def test_read_articles(db_session, test_data):
    articles = await read(db_session)

    assert len(articles) == 2
    assert articles[0].title == 'Test article with author'
    assert articles[0].author_name == 'test_user'
    assert articles[1].author_name == 'Delete user'

@pytest.mark.asyncio
async def test_read_article_detail(db_session, test_data):
    article_id = 1
    article = await read(db_session, article_id)


    assert article.title == 'Test article with author'
    assert article.content == 'Content article 1'
    assert article.author_name == 'test_user'

@pytest.mark.asyncio
async def test_read_non_exists_article_detail(db_session, test_data):
    article_id = 3
    with pytest.raises(HTTPException) as exc:
        await read(db_session, article_id)


    assert exc.value.detail == 'Article not found'
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_update_articles(db_session, test_data):
    article_id = 1
    data = ArticleUpdate(content='New article content')
    current_user = test_data.get('users')
    articles = await update(article_id,current_user[0], db_session, data)
    update_articles = await read(db_session)

    assert articles.get('message') == 'Article updated'
    assert articles.get('status') == 200
    assert update_articles[0].content == 'New article content...'

@pytest.mark.asyncio
async def test_update_articles_by_not_author(db_session, test_data):
    current_user = test_data.get('users')
    article_id = 1
    data = ArticleUpdate(content='New article content')
    articles_before_update = await read(db_session)
    with pytest.raises(HTTPException) as exc_info:
        await update(article_id,current_user[1], db_session, data)
    articles_after_update = await read(db_session)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == 'You don`t have permission'
    assert articles_before_update[0].content == articles_after_update[0].content


@pytest.mark.asyncio
async def test_delete_articles(db_session, test_data):
    article_id = 1
    current_user = test_data.get('users')
    articles_before_delete = await read(db_session)
    articles = await delete(article_id,current_user[0], db_session)
    articles_after_delete = await read(db_session)

    assert articles.get('message') == 'Article deleted'
    assert articles.get('status') == 200
    assert len(articles_before_delete) == 2
    assert len(articles_after_delete) == 1

@pytest.mark.asyncio
async def test_delete_articles_by_not_author(db_session, test_data):
    current_user = test_data.get('users')
    article_id = 2
    articles_before_delete = await read(db_session)
    with pytest.raises(HTTPException) as exc_info:
        await delete(article_id,current_user[0], db_session)
    articles_after_delete = await read(db_session)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == 'You don`t have permission'
    assert len(articles_after_delete) == len(articles_before_delete)