from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.security import get_current_user
from db.models import User
from db.session import get_db
from schemas.article import ArticleCreate, ArticleUpdate
from crud.articles import create, read, update, delete

router = APIRouter(prefix='/articles', tags=['articles'])


@router.post('/create')
async def create_article(
        article: ArticleCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    author_id = current_user.id
    return await create(author_id, article, db)

@router.get('/')
async def show_article(db: Session = Depends(get_db)):
    return await read(db)

@router.patch('/update/{article_id:int}')
async def update_article(
        data: ArticleUpdate,
        article_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await update(data, article_id, current_user, db)

@router.delete('/delete/{article_id:int}')
async def delete_article(
        article_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await delete(article_id, current_user, db)