from typing import List

from fastapi import Depends, FastAPI, HTTPException, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse

from sqlalchemy.orm import Session

from . import crud, models, schemas, database
from .database import SessionLocal, engine

from fastapi.templating import Jinja2Templates

# models.Base.metadata.create_all(bind=engine)

from fastapi.param_functions import Depends
from pydantic import BaseModel, Field
from typing import List, Union, Optional, Dict, Any
from uuid import UUID, uuid4

from datetime import datetime

import io
import os
import numpy as np
from PIL import Image
from os.path import join
from pathlib import Path

import logging
from .detect import run, load_det_model

from .model import efficientnet_b0
from .predict import get_big_prediction, get_small_prediction, get_quantity_prediction, load_big_model, load_small_model, load_quantity_model


app = FastAPI()

MODEL_DIR_PATH = os.path.join(Path(__file__).parent.parent, "ptmodels")

Det_Model = load_det_model(weights=join(MODEL_DIR_PATH, 'best.torchscript.pt'))
Big_Model = load_big_model()
Small_Model  = load_small_model()
Quantity_Model = load_quantity_model()
templates = Jinja2Templates(directory='./templates')


class Food(BaseModel):
    big_label: str
    small_label: str
    xyxy: list
    info: dict


class Intake(BaseModel):
    Foods: List[Food] = Field(default_factory=list)

    def add_food(self, food: Food):
        # add_product는 Product를 인자로 받아서, 해당 id가 이미 존재하는지 체크 => 없다면 products 필드에 추가
        # 업데이트할 때 updated_at을 현재 시각으로 업데이트
        if food.id in [existing_product.id for existing_product in self.products]:
            return self

        self.Foods.append(food)
        self.updated_at = datetime.now()
        return self


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



@app.get("/users/{user}/intakes/")
def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)






@app.post("/users/{user}/intakes/", response_model=schemas.Intake)
async def detect(user: int, files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    xyxys = []
    for file in files:
        image_bytes = await file.read()
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert('RGB')
        img_np = np.array(img)
        h, w, c = img_np.shape
        print(f'img shape : {w, h}')

        xyxys = run(Det_Model, img0=np.array(img.resize((640, 640))))
        foods = []
        for xyxy in xyxys:            
            x1, y1 = int(w*xyxy[0]), int(h*xyxy[1])
            x2, y2 = int(w*xyxy[2]), int(h*xyxy[3])

            cropped_img = img.crop((x1, y1, x2, y2))            

            big_label = get_big_prediction(model=Big_Model, img=cropped_img)
            small_labels = get_small_prediction(img=cropped_img, model_info=Small_Model, cls=big_label)
            quantity = get_quantity_prediction(model=Quantity_Model, img=cropped_img) + 1
        
            name, carbohydrate, protein, fat, sugar, kcal = small_labels
            c, p, f, s, k = [round(float(v) * quantity * 0.2, 2) for v in [carbohydrate, protein, fat, sugar, kcal]]
            info = {'quantity': quantity, 'carbohydrate': c, 'protein': p, 'fat': f, 'sugar': s, 'kcal': k}

            foods = crud.create_food(db=db, category=big_label, name=name, amount=quantity,carbohydrate=carbohydrate, protein=protein, fat=fat, sugar=sugar)

    return crud.create_intake(db=db, foods=foods, user=user)















# 전체 intake 조회
# @app.get("/history/", response_model=List[schemas.Intake])
# def read_intakes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     intakes = crud.get_intakes(db, skip=skip, limit=limit)
#     return intakes



# 유저 히스토리 조회
@app.get("/history/{user}", response_model=List[schemas.Intake])
async def read_intakes(user:int, db: Session = Depends(get_db)):
    history = crud.get_intakes_by_user(db, user=user)
    if not history:
        return {"message": "조회할 데이터가 없습니다."}
    return history
