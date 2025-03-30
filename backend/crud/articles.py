from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from backend.core.decorators import check_article_permission
from backend.crud.user import get_user
from backend.db.models import Article, User
from backend.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse


async def create(author_id: int, article: ArticleCreate, db: Session):
        article = Article(
            title=article.title,
            content=article.content,
            author_id=author_id
        )

        db.add(article)
        await db.commit()
        await db.refresh(article)

        return {'message':'Article create', 'status':status.HTTP_201_CREATED}


async def read(db: Session):
    result = await db.execute(select(Article).order_by(Article.id))
    articles = result.scalars().all()
    article_response = [
        ArticleResponse(
        id=article.id,
        title=article.title,
        content=article.content,
        author_name=(await get_user(db=db, user_id=article.author_id)).full_name,
        created_at=article.created_at,
        update_at=article.update_at
    ) for article in articles]

    return article_response

@check_article_permission(Article)
async def update(article_id: int, current_user: User, db: Session, data: ArticleUpdate):
    result = await db.execute(select(Article).filter(Article.id == article_id))
    article = result.scalars().first()

    update_data: dict = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(article, key, value)

    db.add(article)
    await db.commit()
    await db.refresh(article)

    return {'message':'Article updated', 'status':status.HTTP_200_OK}

@check_article_permission(Article)
async def delete(article_id: int, current_user: User, db: Session):
    result = await db.execute(select(Article).filter(Article.id==article_id))
    article = result.scalars().first()

    await db.delete(article)
    await db.commit()


    return {'message': 'Article deleted', 'status': status.HTTP_200_OK}