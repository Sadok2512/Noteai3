from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import jwt
from datetime import datetime

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret")
MONGO_URI = os.getenv("MONGO_URI")

try:
    client = MongoClient(MONGO_URI)
    db = client["noteai"]
    notes_collection = db["notes"]
except Exception as e:
    print("❌ Erreur MongoDB dans history.py:", e)

security = HTTPBearer()

def decode_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload.get("email")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")

@router.get("/history/{email}")
async def get_user_history(email: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    user_email = decode_token(credentials.credentials)
    if user_email != email:
        raise HTTPException(status_code=403, detail="Accès interdit")

    try:
        notes = list(notes_collection.find({"user_id": email}).sort("uploaded_at", -1))
        history = []
        for note in notes:
            history.append({
                "id": str(note.get("_id")),
                "user_id": note.get("user_id"),
                "filename": note.get("filename"),
                "stored_as": str(note.get("_id")) + ".webm",
                "uploaded_at": note.get("uploaded_at"),
                "size_bytes": note.get("size_bytes", 0),
                "source": note.get("source", "WEB"),
            })
        return history
    except Exception as e:
        print("❌ Erreur chargement historique:", e)
        raise HTTPException(status_code=500, detail="Erreur serveur lors du chargement de l'historique.")