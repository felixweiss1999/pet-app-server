from sqlalchemy.orm import Session
from . import models, schemas
import time
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

def get_filename_by_user(db: Session, userid: str):
    return db.query(models.File).filter(models.File.user == userid).all()

def edit_user(db: Session, user: schemas.UserCreate):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    db_user.birthday = user.birthday
    db_user.intro = user.intro
    db_user.name = user.name
    db_user.password = user.password
    db.commit()
    db.refresh(db_user)
    return db_user



#posts
def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).offset(skip).limit(limit).all()

def get_post_by_id(db: Session, id: int):
    return db.query(models.Post).filter(models.Post.id == id).first()

def create_post(db: Session, post: schemas.PostCreate):
    db_post = models.Post(**post.dict(), timestamp=time.time())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_post_replies(db: Session, postid: int):
    return db.query(models.Post).filter(models.Post.response_to == postid).all()






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



#chat
def create_chat(db: Session, chat: schemas.ChatCreate):
    db_chat = models.Chat(**chat.dict())
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def get_chats_by_user(db: Session, uid: str, uid2: str = None):
    if uid2 is None:
        return db.query(models.Chat).filter(models.Chat.user1 == uid).all() + db.query(models.Chat).filter(models.Chat.user2 == uid).all() 
    return db.query(models.Chat).filter(models.Chat.user1 == uid, models.Chat.user2 == uid2).all() + db.query(models.Chat).filter(models.Chat.user1 == uid2, models.Chat.user2 == uid).all()

def get_chat_by_id(db: Session, chatid: int):
    return db.query(models.Chat).filter(models.Chat.id == chatid).first()

def get_message_by_id(db: Session, messageid: int):
    return db.query(models.Message).filter(models.Message.id == messageid).first()

def create_message(db: Session, message: schemas.MessageCreate):
    db_message = models.Message(**message.dict(), timestamp=time.time())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


#pet

def create_pet(db: Session, pet: schemas.PetCreate):
    db_pet = models.Pet(**pet.dict())
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet

def edit_pet(db: Session, pet: schemas.PetCreate, petid: int):
    db_pet = db.query(models.Pet).filter(models.Pet.id == petid).first()
    db_pet.birthday = pet.birthday
    db_pet.breed = pet.breed
    db_pet.gender = pet.gender
    db_pet.name = pet.name
    db_pet.personality_labels = pet.personality_labels
    db.commit()
    db.refresh(db_pet)
    return db_pet

def get_pet_by_id(db: Session, petid: int):
    return db.query(models.Pet).filter(models.Pet.id == petid).first()




# like
def toggle_like(db: Session, like: schemas.LikeCreate):
    db_like = db.query(models.Like).filter(models.Like.liker == like.liker, models.Like.liked_post == like.liked_post).first()
    if db_like is None:
        db_like = models.Like(**like.dict(), timestamp=time.time())
        db.add(db_like)
        db.commit()
        return 1
    else:
        db.delete(db_like)
        db.commit()
        return 0
    
#follow
def toggle_follow(db: Session, follow: schemas.FollowCreate):
    db_follow = db.query(models.Follow).filter(models.Follow.follower == follow.follower, models.Follow.follows == follow.follows).first()
    if db_follow is None:
        db_follow = models.Follow(**follow.dict(), timestamp=time.time())
        db.add(db_follow)
        db.commit()
        return 1
    else:
        db.delete(db_follow)
        db.commit()
        return 0
