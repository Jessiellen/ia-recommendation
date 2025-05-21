from pydantic import BaseModel
from typing import List

class ProductBase(BaseModel):
    name: str
    description: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    products: List[Product] = []

    class Config:
        orm_mode = True

class Recommendation(BaseModel):
    product_id: int
    product_name: str
    reason: str