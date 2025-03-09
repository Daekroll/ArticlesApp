from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    func
)
from sqlalchemy.orm import relationship

from ..session import Base


class User(Base):

    __tablename__ = 'users'


    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, unique=True, nullable=False)
    hashed_password = Column(String, index=True)
    full_name = Column(String, index=True)
    is_active = Column(Boolean, index=True, default=False)
    created_at = Column(Date, index=True, server_default=func.now())
    avatar = Column(String, index=True, nullable=True)


    articles = relationship('Article', back_populates='author')
    comment = relationship('Comment', back_populates='comentator')