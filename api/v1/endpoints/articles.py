from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from schemas.article import ArticleResponse, ArticleCreate

router = APIRouter(prefix='/articles', tags=['articles'])


@router.post('/', response_model=ArticleResponse)
async def create_article(article: ArticleCreate):
    return article


@router.get('/', response_model=ArticleResponse)
async def create_article(article: ArticleCreate):
    return article