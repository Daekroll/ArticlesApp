from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from backend.core.decorators import check_article_permission
from backend.crud.user import get_user
from backend.db.models import User, Comment
from backend.schemas.comment import CommentCreate, CommentResponse


async def create(author_id: int, comment: CommentCreate, db: Session):
    comment = Comment(
        content=comment.content,
        article_id=comment.article_id,
        author_id=author_id
    )

    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    return {'message': 'Comment successfully added', 'status': status.HTTP_201_CREATED}


async def read(article_id: int, db: Session):
    result = await db.execute(select(Comment).filter(Comment.article_id == article_id).order_by(Comment.id))
    comments = result.scalars().all()
    comments_response = [
        CommentResponse(
            id=comment.id,
            content=comment.content,
            article_id=comment.article_id,
            author_name=(await get_user(db=db, user_id=comment.author_id)).full_name,
            created_at=comment.created_at
        ) for comment in comments]

    return comments_response

@check_article_permission(Comment)
async def delete(comment_id: int, current_user: User, db: Session):
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalars().first()

    await db.delete(comment)
    await db.commit()

    return {'message': 'Comment deleted', 'status': status.HTTP_200_OK}
