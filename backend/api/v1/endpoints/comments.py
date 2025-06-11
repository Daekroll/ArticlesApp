from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from core.security import get_current_user
from db.models import User
from db.session import get_db
from crud.comments import create, read, delete
from schemas.comment import CommentCreate, CommentResponse

router = APIRouter(prefix='/comments')


@router.post('/create',
    status_code=status.HTTP_201_CREATED,
    summary='Создать новый комментарий',
    description="""
    Создает новый комментарий к статье.
    
    Требования:
    - Пользователь должен быть авторизован
    - Аккаунт пользователя должен быть подтвержден
    - Статья должна существовать
    """,
    tags=['Комментарии'],
    responses={
        status.HTTP_201_CREATED: {
            'description': 'Комментарий успешно создан',
            'content': {
                'application/json': {
                    'example': {
                        'message': 'Comment successfully added',
                        'status': status.HTTP_201_CREATED
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            'description': 'Ошибка валидации данных',
            'content': {
                'application/json': {
                    'example': {'detail': 'Validation error'}
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Пользователь не авторизован',
            'content': {
                'application/json': {
                    'example': {'detail': 'Not authenticated'}
                }
            }
        },
        status.HTTP_403_FORBIDDEN: {
            'description': 'Аккаунт не подтвержден',
            'content': {
                'application/json': {
                    'example': {
                        'status_code': status.HTTP_403_FORBIDDEN,
                        'detail': 'You need to confirm email'
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            'description': 'Статья не найдена',
            'content': {
                'application/json': {
                    'example': {
                        'status_code': status.HTTP_404_NOT_FOUND,
                        'detail': 'Article not found'
                    }
                }
            }
        }
    })
async def create_comment(
        comment: CommentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await create(current_user, comment, db)


@router.get('/{article_id:int}',
    response_model=List[CommentResponse],
    status_code=status.HTTP_200_OK,
    summary='Получить комментарии к статье',
    description="""
    Возвращает все комментарии для указанной статьи.

    Особенности:
    - Комментарии сортируются по дате создания (от старых к новым)
    - Для удаленных пользователей отображается специальное имя
    - Возвращает пустой список, если комментариев нет
    """,
    tags=['Комментарии'],
    responses={
        status.HTTP_200_OK: {
            'description': 'Список комментариев',
            'content': {
                'application/json': {
                    'example': [
                        {
                            'id': 1,
                            'content': 'Отличная статья!',
                            'article_id': 5,
                            'author_name': 'Иван Иванов',
                            'created_at': '2023-01-01T12:00:00'
                        },
                        {
                            'id': 2,
                            'content': 'Спасибо за полезный материал',
                            'article_id': 5,
                            'author_name': 'Петр Петров',
                            'created_at': '2023-01-02T10:30:00'
                        }
                    ]
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            'description': 'Статья не найдена',
            'content': {
                'application/json': {
                    'example': {
                        'status_code': status.HTTP_404_NOT_FOUND,
                        'detail': 'Article not found'
                    }
                }
            }
        }
    })
async def show_comment(article_id: int, db: Session = Depends(get_db)):
    return await read(article_id, db)


@router.delete('/delete/{comment_id:int}',
    status_code=status.HTTP_200_OK,
    summary='Удалить комментарий',
    description="""
    Удаляет комментарий по его ID.
    
    Требования:
    - Пользователь должен быть автором комментария или администратором
    - Пользователь должен быть авторизован
    - Комментарий должен существовать
    """,
    tags=['Комментарии'],
    responses={
        status.HTTP_200_OK: {
            'description': 'Комментарий успешно удален',
            'content': {
                'application/json': {
                    'example': {
                        'message': 'Comment deleted',
                        'status': status.HTTP_200_OK
                    }
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Пользователь не авторизован',
            'content': {
                'application/json': {
                    'example': {'detail': 'Not authenticated'}
                }
            }
        },
        status.HTTP_403_FORBIDDEN: {
            'description': 'Нет прав для удаления комментария',
            'content': {
                'application/json': {
                    'example': {
                        'status_code': status.HTTP_403_FORBIDDEN,
                        'detail': 'You don`t have permission'
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            'description': 'Комментарий не найден',
            'content': {
                'application/json': {
                    'example': {'detail': 'Comment not found'}
                }
            }
        }
    })
async def delete_comment(
        comment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await delete(comment_id, current_user, db)