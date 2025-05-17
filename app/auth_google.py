from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import jwt  # Assure-toi que c'est bien le module PyJWT installé
import os
import requests

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret")

class GoogleToken(BaseModel):
    token: str

def verify_google_token(id_token: str):
    try:
        response = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}")
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Token Google invalide")
        data = response.json()
        if data["aud"] != GOOGLE_CLIENT_ID:
            raise HTTPException(status_code=401, detail="Audience non autorisée")
        return data
    except Exception as e:
        print("❌ Erreur vérification Google Token:", str(e))
        raise HTTPException(status_code=401, detail="Échec de vérification Google")

@router.post("/google")
def auth_google(payload: GoogleToken):
    data = verify_google_token(payload.token)
    email = data.get("email")

    if not email:
        raise HTTPException(status_code=400, detail="Email non trouvé dans token")

    try:
        jwt_token = jwt.encode({"email": email}, JWT_SECRET, algorithm="HS256")
        if isinstance(jwt_token, bytes):
            jwt_token = jwt_token.decode("utf-8")
    except Exception as e:
        print("❌ Erreur génération JWT:", str(e))
        raise HTTPException(status_code=500, detail="Erreur création JWT")

    return {
        "token": jwt_token,
        "email": email
    }
