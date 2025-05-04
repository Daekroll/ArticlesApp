import logging

from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from backend.core.decorators import check_user_permission, check_user_is_active
from backend.crud.user import get_user
from backend.db.models import User, Comment
from backend.schemas.comment import CommentCreate, CommentResponse

console_logger = logging.getLogger('console_logger')

@check_user_is_active(schema=CommentCreate)
async def create(
        author: User,
        comment: CommentCreate,
        db: Session
):
    comment = Comment(
        content=comment.content,
        article_id=comment.article_id,
        author_id=author.id
    )

    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    console_logger.info('Comment successfully added')
    return {'message': 'Comment successfully added', 'status': status.HTTP_201_CREATED}


async def read(article_id: int, db: Session):
    result = await db.execute(select(Comment).filter(Comment.article_id == article_id).order_by(Comment.id))
    comments = result.scalars().all()
    comments_response = []

    for comment in comments:
        if comment.author_name is not None:
            user = await get_user(db=db, user_id=comment.author_id)
            author_name = user.full_name
        else:
            author_name = 'Delete user'
        comments_response.append(
            CommentResponse(
                id=comment.id,
                content=comment.content,
                article_id=comment.article_id,
                author_name=author_name,
                created_at=comment.created_at
            ))

    return comments_response

@check_user_permission(Comment)
async def delete(comment_id: int, current_user: User, db: Session):
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalars().first()

    await db.delete(comment)
    await db.commit()
    console_logger.info('Comment deleted')
    return {'message': 'Comment deleted', 'status': status.HTTP_200_OK}
