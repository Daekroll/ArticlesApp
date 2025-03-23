from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from crud.user import get_user
from db.models import User, Comment
from schemas.comment import CommentCreate, CommentResponse


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
            content=comment.content,
            article_id=comment.article_id,
            author_name=(await get_user(db=db, user_id=comment.author_id)).full_name,
            created_at=comment.crated_at
        ) for comment in comments]

    return comments_response


async def delete(comment_id: int, current_user: User, db: Session):
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Comment not found'
        )
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You don`t have permission'
        )

    await db.delete(comment)
    await db.commit()

    return {'message': 'Comment deleted', 'status': status.HTTP_200_OK}
