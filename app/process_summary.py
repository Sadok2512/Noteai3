from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
import os, traceback

router = APIRouter()

# Connexion MongoDB sécurisée
try:
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        raise ValueError("MONGO_URI est manquant.")
    client = MongoClient(MONGO_URI)
    db = client["noteai"]
    notes_collection = db["notes"]
except Exception as conn_err:
    print("❌ Erreur de connexion MongoDB dans process_summary:", conn_err)

@router.post("/process-summary/{file_id}")
async def process_summary(file_id: str):
    try:
        print("🧠 Traitement du fichier:", file_id)

        # Simule traitement IA
        fake_transcription = "Ceci est une transcription simulée."
        fake_summary = "Résumé automatique généré."
        fake_tasks = ["Tâche 1", "Tâche 2"]

        result = notes_collection.update_one(
            {"_id": file_id},
            {
                "$set": {
                    "transcription": fake_transcription,
                    "summary": fake_summary,
                    "tasks": fake_tasks
                }
            }
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Note non trouvée")

        print("✅ Traitement terminé pour:", file_id)
        return {"message": "Traitement terminé", "file_id": file_id}

    except Exception as e:
        print("❌ Erreur traitement:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Erreur traitement.")