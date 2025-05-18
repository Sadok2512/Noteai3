from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
import os, traceback
import gridfs

router = APIRouter()

try:
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        raise ValueError("MONGO_URI est manquant.")
    client = MongoClient(MONGO_URI)
    db = client["noteai"]
    fs = gridfs.GridFS(db)
    notes_collection = db["notes"]
except Exception as conn_err:
    print("❌ Erreur de connexion MongoDB:", conn_err)

def fake_transcribe_audio(audio_bytes):
    return "Ceci est une transcription simulée."

def fake_summarize(text):
    return "Résumé généré automatiquement.", ["Tâche 1", "Tâche 2"]

@router.post("/process-summary/{stored_as}")
async def process_summary(stored_as: str):
    try:
        note = notes_collection.find_one({"stored_as": stored_as})
        if not note:
            raise HTTPException(status_code=404, detail="Note non trouvée")

        file = fs.find_one({"filename": stored_as})
        if not file:
            raise HTTPException(status_code=404, detail="Fichier audio introuvable")

        audio_bytes = file.read()
        transcription = fake_transcribe_audio(audio_bytes)
        summary, tasks = fake_summarize(transcription)

        notes_collection.update_one(
            {"stored_as": stored_as},
            {"$set": {
                "transcription": transcription,
                "summary": summary,
                "tasks": tasks
            }}
        )

        return {
            "message": "Traitement réussi",
            "transcription": transcription,
            "summary": summary,
            "tasks": tasks
        }

    except Exception as e:
        print("❌ ERREUR PROCESS SUMMARY:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Erreur traitement")
