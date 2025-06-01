import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from async_asgi_testclient import TestClient

from core.security import get_password_hash, generate_timestamp_link, create_access_token
from db.models.article import Article
from db.models.user import User
from db.models.comment import Comment
from db.session import Base, get_db
from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.users import router as users_router
from api.v1.endpoints.articles import router as articles_router
from api.v1.endpoints.comments import router as comments_router
from crud.user import add_token




app = FastAPI()
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(articles_router)
app.include_router(comments_router)

client = TestClient(app)

TEST_DATABASE_URL = f'postgresql+asyncpg://test_user:1234@localhost/test_db'


@pytest.fixture(scope="function")
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def auth_client(db_session, test_data):
    async def _auth_client(user_index=3):
        test_user = test_data['users'][user_index]
        token = create_access_token({'sub':test_user.email})
        await add_token(token, db_session)
        return TestClient(
            app,
            headers={"Authorization": f"Bearer {token}"}
        )
    return _auth_client


@pytest.fixture(scope="function")
async def test_data(db_session):
    full_link = generate_timestamp_link()
    rand_part, *_ = full_link.split('_')
    test_user_hashed_password = get_password_hash('Qwerty147')
    test_users = [User(
        email='test_user@mail.ru',
        hashed_password=test_user_hashed_password,
        full_name='test_user',
        activate_link=None,
        is_active=True
    ),
    User(
        email='test_user1@mail.ru',
        hashed_password=test_user_hashed_password,
        full_name='test_user1',
        activate_link=None,
        is_active=True
    ),
    User(
        email='test_user2@mail.ru',
        hashed_password=test_user_hashed_password,
        full_name='test_user2',
        activate_link=rand_part,
        is_active=False
    ),
    User(
        email='test_admin_user@mail.ru',
        hashed_password=test_user_hashed_password,
        full_name='test_admin_user',
        activate_link=None,
        is_active=True,
        is_staff=True
    ),
    ]

    db_session.add_all(test_users)
    await db_session.flush()

    articles = [
        Article(
            title='Test article with author',
            content='Content article 1',
            author_id=1),
        Article(
            title='Test article without author',
            content='Content article 2',
            author_id=None)
    ]

    db_session.add_all(articles)
    await db_session.flush()

    comments = [
        Comment(
            content='Comment 1',
            article_id=1,
            author_id=1
        ),
        Comment(
            content='Comment 2',
            article_id=1,
            author_id=2
        ),
        Comment(
            content='Comment 3',
            article_id=2,
            author_id=4
        )
    ]

    db_session.add_all(comments)
    await db_session.commit()
    for test_user in test_users:
        await db_session.refresh(test_user)
    for article in articles:
        await db_session.refresh(article)
    for comment in comments:
        await db_session.refresh(comment)

    return {'users' : test_users, 'full_link':full_link}