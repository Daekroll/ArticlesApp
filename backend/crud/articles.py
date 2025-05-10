import logging

from fastapi import status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from backend.core.decorators import check_user_permission, check_user_is_active
from backend.crud.user import get_user
from backend.db.models import Article, User
from backend.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse

console_logger = logging.getLogger('console_logger')

async def get_articles(db: Session, article_id: int = None):
    if article_id is None:
        result = await db.execute(select(Article).order_by(Article.id))
        articles = result.scalars().all()
        return articles


    result = await db.execute(select(Article).filter(Article.id == article_id))
    articles = result.scalars().first()
    if articles is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='article not found'
        )
    return articles

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
    console_logger.info('Article read start')
    articles = await get_articles(db)
    console_logger.info(f'execute db{articles}')

    article_response = []

    for article in articles:
        console_logger.info(f'Enter in for')
        if article.author_id is not None:
            console_logger.info(f'Enter in if')
            user = await get_user(db=db, user_id=article.author_id)
            author_name = user.full_name
        else:
            author_name = 'Delete user'
        console_logger.info(f'Change name{author_name}')
        article_response.append(
            ArticleResponse(
            id=article.id,
            title=article.title,
            content=article.content,
            author_name=author_name,
            created_at=article.created_at,
            update_at=article.update_at
            ))
    console_logger.info('Article read end')
    return article_response

@check_user_permission(Article)
async def update(article_id: int, current_user: User, db: Session, data: ArticleUpdate):
    article = await get_articles(db, article_id)

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
    article = await get_articles(db, article_id)

    await db.delete(article)
    await db.commit()

    console_logger.info('Article deleted')
    return {'message': 'Article deleted', 'status': status.HTTP_200_OK}