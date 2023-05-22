from sqlalchemy.orm import Session
from . import models, schemas

#user
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit() #saves on disk
    db.refresh(db_user) #refresh instance so that new additions (like new id) take effect in code as well
    return db_user


#posts
def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).offset(skip).limit(limit).all()

def get_post_by_id(db: Session, id: int):
    return db.query(models.Post).filter(models.Post.id == id).first()

def create_post(db: Session, post: schemas.PostCreate):
    db_post = models.Post(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_post_replies(db: Session, postid: int):
    return db.query(models.Post).filter(models.Post.response_to == postid).all()

def get_filename_by_post(db: Session, postid: int):
    return db.query(models.File).filter(models.File.post == postid).first()

#file
def get_filename_by_id(db: Session, fileid: int):
    return db.query(models.File).filter(models.File.id == fileid).first()

def create_file(db: Session, file: schemas.FileCreate):
    db_file = models.File(**file.dict())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def set_filepath(db: Session, fileid: int, filepath: str):
    db_file = db.query(models.File).filter(models.File.id == fileid).first()
    db_file.file_path = filepath
    db.commit()
    db.refresh(db_file)
    return db_file

def delete_file(db: Session, fileid: int):
    db_file = db.query(models.File).filter(models.File.id == fileid).first()
    db.delete(db_file)
    db.commit()



