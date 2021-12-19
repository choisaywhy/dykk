from typing import Optional, List
from fastapi import Depends, FastAPI, HTTPException, Form, Request, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.param_functions import Depends
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import List, Union, Optional, Dict, Any
from datetime import datetime
from app.model import MyEfficientNet, get_model, get_config, predict_from_image_byte
from sqlalchemy.orm import Session, sessionmaker
import sqlalchemy.orm.session



sql_app.models.Base.metadata.create_all(bind=sql_app.database.engine)
Det_Model = get_detect_model()
Big_Model = get_big_model()

app = FastAPI()

# 유저 디비 접근
# 유저 회원가입
# 유저 칼로리 정보 저장
# 모델 올리기 intake 저장 등등등
# 유저 데이터 불러오기

# signin(POST)
# signup(POST)
# save_intake(POST)    : 
# get_history(GET)     : 먹었던 음식 정보 그래프화




# Dependency
def get_db():
    db = sql_app.database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users",response_model=sql_app.schemas.User)
def create_user2(user:sql_app.schemas.UserCreate, db: Session = Depends(get_db)): # 무조건 typing을 해줘야 에러가 발생하지 않음
    db_user = sql_app.crud.get_user_by_email(db, email=user.email)

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return sql_app.crud.create_user(db=db, user=user)



# 유저 히스토리 조회
@app.get("/history/{user_id}", description="user intake 정보를 가져옵니다")
async def get_history(user_id: UUID) -> Union[Intake, dict]:
    history = get_intake_by_user_id(user_id=user_id)
    if not history:
        return {"message": "조회할 데이터가 없습니다."}
    return history

def get_intake_by_user_id(user_id: UUID) -> Optional[Intake]:
    return next((intake for intake in intakes if intake.user_id == User.user_id), None)
# intakes는 intake db를 참조할것


# 모델 서빙 (이미지 전달받아서 모델 돌리고 결과 출력)
@app.post("/predict/", description="주문을 요청합니다")
async def make_intake(files: List[UploadFile] = File(...),
                     model: MyEfficientNet = Depends(get_model),
                     config: Dict[str, Any] = Depends(get_config)):
    foods = []
    for file in files:
        image_bytes = await file.read()
        inference_result = predict_from_image_byte(model=model, image_bytes=image_bytes, config=config)
        food = InferenceImageProduct(result=inference_result) 
        foods.append(food)

    new_intake = Intake(food_key=foods)
    intakes.append(new_intake)
    return new_intake


