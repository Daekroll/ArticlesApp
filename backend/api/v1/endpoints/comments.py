from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.security import get_current_user
from backend.db.models import User
from backend.db.session import get_db
from backend.crud.comments import create, read, delete
from backend.schemas.comment import CommentCreate

router = APIRouter(prefix='/comments', tags=['comments'])


@router.post('/create')
async def create_comment(
        comment: CommentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await create(current_user, comment, db)


@router.get('/{article_id:int}')
async def show_comment(article_id: int, db: Session = Depends(get_db)):
    return await read(article_id, db)


@router.delete('/delete/{comment_id:int}')
async def delete_comment(
        comment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await delete(comment_id, current_user, db)