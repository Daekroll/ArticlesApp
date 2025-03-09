from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    ForeignKey
)
from sqlalchemy.orm import relationship

from ..session import Base


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False, index=True)
    article_id = Column(Integer, ForeignKey('articles.id') ,index=True)
    author_id = Column(Integer, ForeignKey('users.id') ,index=True)
    crated_at = Column(DateTime, server_default=func.now(), index=True)

    commentator = relationship('User', back_populates='comment')
    article = relationship('Article', back_populates='comments')