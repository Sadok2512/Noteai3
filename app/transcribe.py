from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pymongo import MongoClient
from bson import ObjectId
import os
import datetime

router = APIRouter()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["noteai"]
notes_collection = db["notes"]

@router.post("/transcribe-replicate")
async def transcribe_replicate(
    file: UploadFile = File(...),
    user_id: str = Form(...)
):
    try:
        content = await file.read()
        file_id_str = str(ObjectId())  # ID factice

        # Simuler transcription ici (à remplacer par vrai appel API)
        transcription = "[Transcription simulée]"
        note_data = {
            "_id": file_id_str,
            "user_id": user_id,
            "filename": file.filename,
            "transcription": transcription,
            "uploaded_at": datetime.datetime.utcnow().isoformat(),
        }

        notes_collection.insert_one(note_data)
        return {
            "id": file_id_str,
            "transcription": transcription,
            "filename": file.filename,
            "user_id": user_id
        }

    except Exception as e:
        print("❌ Erreur transcribe:", e)
        raise HTTPException(status_code=500, detail="Erreur interne lors de la transcription")
