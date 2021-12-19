from sqlalchemy.orm import Session
from . import models, schemas


def get_user(db: Session, id: int):
    return db.query(models.User).filter(models.User.id == id).first()

def get_user_by_nickname(db: Session, nickname: str):
    return db.query(models.User).filter(models.User.nickname == nickname).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, nickname: str, password: str, height:float, weight:float):
    fake_hashed_password = password + "notreallyhashed"
    dailykcal = height+weight ##### 권장섭취랑 계산 구문 넣기
    db_user = models.User(nickname=nickname, hashed_password=fake_hashed_password, dailykcal= dailykcal)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



def get_intakes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Intake).offset(skip).limit(limit).all()

def get_intakes_by_user(db: Session, user:int):
    return db.query(models.Intake).filter(models.User.id == user).all()

def create_intake(db: Session, intake: schemas.IntakeCreate, user: int):
    ## 서빙 후 모델 저장하기
    db_intake = models.Intake(**intake.dict(), user=user)
    db.add(db_intake)
    db.commit()
    db.refresh(db_intake)
    return db_intake

