from typing import List

from fastapi import Depends, FastAPI, HTTPException, UploadFile, File, Request, Form
from sqlalchemy.orm import Session

from . import crud, models, schemas, database
from .database import SessionLocal, engine

from fastapi.templating import Jinja2Templates

# models.Base.metadata.create_all(bind=engine)

from fastapi.param_functions import Depends
from pydantic import BaseModel, Field
from typing import List, Union, Optional, Dict, Any

from datetime import datetime

# import io
# import numpy as np
# from PIL import Image

# from model import efficientnet_b0 
# from predict import run, get_class_model, get_detect_model, predict_from_image_byte, get_big_model, predict_big_class
# from utils import get_config



app = FastAPI()
# Det_Model = get_detect_model()
# Big_Model = get_big_model()
templates = Jinja2Templates(directory='./templates')


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class InferenceImageProduct(schemas.Food):
    name: str = Optional[str]

class DetectedImage(schemas.Food):
    name: str = Optional[str]
    xywh: Optional[List]
    result: Optional[List]


# 회원가입 창 띄우기 query parameter
@app.get("/signup/")
def get_signup_form(request: Request):
    return templates.TemplateResponse('signup_form.html', context={'request': request})

@app.post("/signup/", response_model=schemas.User)
def create_user(nickname: str = Form(...), password: str = Form(...), height: str = Form(...),weight: str = Form(...), db: Session = Depends(get_db)):
    db_user = crud.get_user_by_nickname(db, nickname=nickname)
    if db_user:
        raise HTTPException(status_code=400, detail="user id already registered")
    return crud.create_user(db=db, nickname=nickname, password=password, height= height, weight=weight)


# 로그인 창 띄우기 query parameter
@app.get("/signin/")
def get_login_form(request: Request):
    return templates.TemplateResponse('login_form.html', context={'request': request})

# 로그인
@app.post("/signin/", response_model=schemas.User)
def signin(nickname: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_user = crud.get_user_by_nickname(db, nickname=nickname)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        if db_user.hashed_password == password+"notreallyhashed":
            return db_user
        else :
            raise HTTPException(status_code=404, detail="password incorrect")


#### create intakes 서빙 연결 요망
@app.post("/users/{user}/intakes/", response_model=schemas.Intake)
def create_intake(
    user: int, intake: schemas.IntakeCreate, db: Session = Depends(get_db)
):
    return crud.create_intake(db=db, intake=intake, user=user)


@app.get("/history/{user}/", response_model=List[schemas.Intake])
def read_intakes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    intakes = crud.get_intakes(db, skip=skip, limit=limit)
    return intakes


# 유저 히스토리 조회
@app.get("/history/{user}", response_model=List[schemas.Intake])
async def read_intakes(user:int, db: Session = Depends(get_db)):
    history = crud.get_intakes_by_user(db, user=user)
    if not history:
        return {"message": "조회할 데이터가 없습니다."}
    return history
