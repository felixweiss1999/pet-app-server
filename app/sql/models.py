from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base

#classes that inherit from Base are the SQLAlchemy models!
class User(Base):
    __tablename__ = "users"
    email = Column(String, primary_key=True, index=True)
    password = Column(String)
    name = Column(String)
    profile_picture = Column(Integer, ForeignKey("photos.id"))
    intro = Column(String)
    birthday = Column(String)
    posts = relationship("Post", back_populates="owner")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(String, ForeignKey("users.email"), nullable=False)
    response_to = Column(Integer, ForeignKey("posts.id"), nullable=True)
    content = Column(String)
    picture = Column(Integer, ForeignKey("photos.id"), nullable=True)
    like_count = Column(Integer, default=0)
    owner = relationship("User", back_populates="posts")

class Photo(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True, index=True)
    post = Column(Integer, ForeignKey("posts.id"))
    file_path = Column(String)
