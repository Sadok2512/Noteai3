from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
import jwt
import os

router = APIRouter()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["noteai"]
users_collection = db["users"]

SECRET_KEY = os.getenv("JWT_SECRET", "secret123")

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login_user(data: LoginRequest):
    user = users_collection.find_one({"email": data.email, "password": data.password})
    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe invalide.")
    user_id = str(user["_id"])
    token = jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm="HS256")
    return {"token": token, "email": user["email"], "user_id": user_id}