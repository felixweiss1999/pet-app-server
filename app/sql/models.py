from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base

#classes that inherit from Base are the SQLAlchemy models!
class Follow(Base):
    __tablename__ = "followings"
    follower = Column(String, ForeignKey("users.email"), primary_key=True)
    follows = Column(String, ForeignKey("users.email"), primary_key=True)
    timestamp = Column(Integer)

class User(Base):
    __tablename__ = "users"
    email = Column(String, primary_key=True, index=True)
    password = Column(String)
    name = Column(String)
    intro = Column(String)
    birthday = Column(String)
    posts = relationship("Post", back_populates="owner")
    pets = relationship("Pet", back_populates="owneruser")
    follows = relationship("Follow", foreign_keys=[Follow.follower])
    followed_by = relationship("Follow", foreign_keys=[Follow.follows])
    

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(String, ForeignKey("users.email"), nullable=False)
    response_to = Column(Integer, ForeignKey("posts.id"), nullable=True)
    content = Column(String)
    owner = relationship("User", back_populates="posts")
    files = relationship("File", back_populates="ownerpost")
    likes = relationship("Like", back_populates="likedpost")

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    post = Column(Integer, ForeignKey("posts.id"), nullable=True)
    user = Column(String, ForeignKey("users.email"), nullable=True)
    message = Column(Integer, ForeignKey("messages.id"), nullable=True)
    pet = Column(Integer, ForeignKey("pets.id"), nullable=True)
    file_path = Column(String, nullable=True)
    file_ending = Column(String)
    ownerpost = relationship("Post", back_populates="files")
    ownermessage = relationship("Message", back_populates="files")
    ownerpet = relationship("Pet", back_populates="files")

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True)
    user1 = Column(String, ForeignKey("users.email"), nullable=False)
    user2 = Column(String, ForeignKey("users.email"), nullable=False)
    messages = relationship("Message", back_populates="ownerchat")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    chat = Column(Integer, ForeignKey("chats.id"), nullable=False)
    owner = Column(String, ForeignKey("users.email"), nullable=False)
    content = Column(String)
    timestamp = Column(Integer, nullable=False)
    files = relationship("File", back_populates="ownermessage")
    ownerchat = relationship("Chat", back_populates="messages")

class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer, primary_key=True)
    owner = Column(String, ForeignKey("users.email"), nullable=False)
    name = Column(String)
    breed = Column(String)
    gender = Column(String)
    birthday = Column(String)
    personality_labels = Column(String)
    files = relationship("File", back_populates="ownerpet")
    owneruser = relationship("User", back_populates="pets")

class Like(Base):
    __tablename__ = "likes"
    liker = Column(String, ForeignKey("users.email"), primary_key=True)
    liked_post = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    likedpost = relationship("Post", back_populates="likes")

