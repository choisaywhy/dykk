from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from typing import List
from datetime import datetime
from .database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    foods_rel = relationship("Food", back_populates="category_rel")


class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(Integer, ForeignKey("categories.id"))
    name = Column(String)
    kcal = Column(Float)
    carbohydrate = Column(Float)
    protein = Column(Float)
    fat = Column(Float)
    sugar = Column(Float)
    amount = Column(Integer)

    category_rel = relationship("Category", back_populates="foods_rel")
    intakes_rel = relationship("Intake", back_populates="foods_rel")



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    hashed_password = Column(String)
    nickname = Column(String, unique=True, index=True)
    dailykcal = Column(Float)
    is_active = Column(Boolean, default=True)

    intakes_rel = relationship("Intake", back_populates="user_rel")


class Intake(Base):
    __tablename__ = "intakes"

    id = Column(Integer, primary_key=True, index=True)
    foods = Column(Integer, ForeignKey("foods.id"))
    user = Column(Integer, ForeignKey("users.id"))
    date = Column(String, default=datetime.now())

    foods_rel = relationship("Food", back_populates="intakes_rel")
    user_rel = relationship("User", back_populates="intakes_rel")


