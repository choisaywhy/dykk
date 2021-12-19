from typing import List
from datetime import datetime
from typing import List

from pydantic import BaseModel # 객체 타입설정



class FoodBase(BaseModel):
    name: str
    kcal: float
    carbohydrate : float
    protein : float
    fat : float
    sugar : float

class FoodCreate(FoodBase):
    pass

class Food(FoodBase):
    id: int
    category: int

    class Config:
        orm_mode = True


class CategoryBase(BaseModel): # optional한 필드
    name: str

class CategoryCreate(CategoryBase): # 생성 시 받아야하는 필드
    pass

class Category(CategoryBase): # 자동 생성
    id : int
    foods_rel: List[Food] = []

    class Config:
        orm_mode = True



class IntakeBase(BaseModel):
    date : datetime

class IntakeCreate(IntakeBase):
    pass

class Intake(IntakeBase):
    id : int
    foods : List[Food]
    user : int

    class Config:
        orm_mode = True



class UserBase(BaseModel):
    nickname : str
    dailykcal : float


class UserCreate(UserBase):
    password : str
    height: float
    weight: float


class User(UserBase):
    id : str
    is_active : bool
    intakes_rel: List[Intake] = []
    
    class Config:
        orm_mode = True
