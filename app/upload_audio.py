from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pymongo import MongoClient
import os, datetime, gridfs, traceback, uuid

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
async def upload_audio(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    custom_name: str = Form(""),
    comment: str = Form("")
):
    try:
        print("🎤 Tentative d'upload audio")
        print("🔹 Fichier:", file.filename)
        print("🔹 User ID:", user_id)

        if not file or not user_id:
            raise HTTPException(status_code=400, detail="Fichier ou user_id manquant")

        # Générer un identifiant unique pour stored_as
        stored_as = str(uuid.uuid4())

        # Lire le contenu pour la taille, puis remettre le curseur au début
        content = await file.read()
        size_bytes = len(content)
        file.file.seek(0)

        # Sauvegarde dans GridFS
        audio_id = fs.put(file.file, filename=stored_as, content_type=file.content_type)

        # Choisir le bon nom à enregistrer
        final_filename = custom_name if custom_name else file.filename

        # Préparation du document MongoDB
        note_doc = {
            "stored_as": stored_as,
            "filename": final_filename,
            "content_type": file.content_type,
            "size_bytes": size_bytes,
            "uploaded_at": datetime.datetime.utcnow().isoformat(),
            "source": "WEB",
            "summary": "Résumé en attente.",
            "transcription": "Transcription en attente.",
            "tasks": [],
            "user_id": user_id,
            "comment": comment
        }

        notes_collection.insert_one(note_doc)
        print("✅ Note sauvegardée avec stored_as:", stored_as)
        return { "message": "Upload réussi", "stored_as": stored_as }

    except Exception as e:
        print("❌ Erreur lors de l'upload:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Erreur serveur lors de l'upload.")
