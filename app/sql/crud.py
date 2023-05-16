from sqlalchemy.orm import Session
from . import models, schemas


def get_user(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_public_user(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email, password=user.password)
    db.add(db_user)
    db.commit() #saves on disk
    db.refresh(db_user) #refresh instance so that new additions (like new id) take effect in code as well
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

def create_user_item(db: Session, item: schemas.ItemCreate, user_email: str):
    db_item = models.Item(**item.dict(), owner_id=user_email) #the dict thing only works if all key value pairs match!
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item