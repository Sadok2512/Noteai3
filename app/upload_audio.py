from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pymongo import MongoClient
import os, datetime, gridfs, traceback

router = APIRouter()

# Connexion MongoDB sécurisée
try:
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        raise ValueError("MONGO_URI est manquant dans les variables d'environnement.")
    client = MongoClient(MONGO_URI)
    db = client["noteai"]
    fs = gridfs.GridFS(db)
    notes_collection = db["notes"]
except Exception as conn_err:
    print("❌ Erreur de connexion MongoDB:", conn_err)

@router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...), user_id: str = Form(...), custom_name: str = Form(""), comment: str = Form("")):
    try:
        print("🎤 Tentative d'upload audio")
        print("🔹 Fichier:", file.filename)
        print("🔹 User ID:", user_id)

        if not file or not user_id:
            raise HTTPException(status_code=400, detail="Fichier ou user_id manquant")

        content = await file.read()
        file_id = fs.put(content, filename=file.filename, content_type=file.content_type)
        file_id_str = str(file_id)

        metadata = {
            "_id": file_id_str,
            "user_id": user_id,
            "filename": file.filename,
            "custom_name": custom_name,
            "comment": comment,
            "uploaded_at": datetime.datetime.utcnow().isoformat(),
            "content_type": file.content_type,
            "size_bytes": len(content),
            "summary": "En attente",
            "transcription": "",
            "tasks": [],
            "source": "WEB"
        }

        notes_collection.insert_one(metadata)
        print("✅ Fichier enregistré avec ID:", file_id_str)
        return {"file_id": file_id_str, "message": "Upload réussi."}

    except Exception as e:
        print("❌ Erreur upload_audio:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Erreur lors de l'upload.")