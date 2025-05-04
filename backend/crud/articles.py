import logging

from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from backend.core.decorators import check_user_permission, check_user_is_active
from backend.crud.user import get_user
from backend.db.models import Article, User
from backend.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse

console_logger = logging.getLogger('console_logger')

@check_user_is_active(schema=ArticleCreate)
async def create(
        author: User,
        article: ArticleCreate,
        db: Session
):
        article = Article(
            title=article.title,
            content=article.content,
            author_id=author.id
        )

        db.add(article)
        await db.commit()
        await db.refresh(article)
        console_logger.info('Article create')
        return {'message':'Article create', 'status':status.HTTP_201_CREATED}


async def read(db: Session):
    result = await db.execute(select(Article).order_by(Article.id))
    articles = result.scalars().all()
    article_response = []

    for article in articles:
        if article.author_name is not None:
            user = await get_user(db=db, user_id=article.author_id)
            author_name = user.full_name
        else:
            author_name = 'Delete user'
        article_response.append(
            ArticleResponse(
            id=article.id,
            title=article.title,
            content=article.content,
            author_name=author_name,
            created_at=article.created_at,
            update_at=article.update_at
            ))

    return article_response

@check_user_permission(Article)
async def update(article_id: int, current_user: User, db: Session, data: ArticleUpdate):
    result = await db.execute(select(Article).filter(Article.id == article_id))
    article = result.scalars().first()

    update_data: dict = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(article, key, value)

    db.add(article)
    await db.commit()
    await db.refresh(article)
    console_logger.info('Article updated')
    return {'message':'Article updated', 'status':status.HTTP_200_OK}

@check_user_permission(Article)
async def delete(article_id: int, current_user: User, db: Session):
    result = await db.execute(select(Article).filter(Article.id==article_id))
    article = result.scalars().first()

    await db.delete(article)
    await db.commit()

    console_logger.info('Article deleted')
    return {'message': 'Article deleted', 'status': status.HTTP_200_OK}