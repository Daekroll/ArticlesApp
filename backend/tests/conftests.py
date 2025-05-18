import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from backend.core.security import get_password_hash
from backend.db.models.article import Article
from backend.db.models.user import User
from backend.db.models.comment import Comment
from backend.db.session import Base

TEST_DATABASE_URL = f'postgresql+asyncpg://test_user:1234@localhost/test_db'


@pytest.fixture(scope='function')
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    db = async_session()

    yield db

    await db.close()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_data(db_session):
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
        activate_link=None,
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

    return {'users' : test_users}