from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
import os, traceback, gridfs, tempfile, requests, time

router = APIRouter()

# Connexion MongoDB
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

def transcribe_with_replicate(audio_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp:
        temp.write(audio_bytes)
        temp_path = temp.name

    # Upload vers file.io
    with open(temp_path, "rb") as f:
        res = requests.post("https://file.io", files={"file": f})
        try:
            res_json = res.json()
            print("🔗 file.io response:", res_json)
        except Exception as e:
            print("❌ Erreur parsing JSON file.io:", res.text)
    raise Exception("file.io a échoué : réponse invalide")

file_url = res_json.get("link")
if not file_url:
    raise Exception("Lien file.io non trouvé dans la réponse")

    if not file_url:
        raise Exception("Échec de l'upload vers file.io")

    headers = {
        "Authorization": f"Token {os.environ['REPLICATE_API_TOKEN']}",
        "Content-Type": "application/json"
    }

    # Démarrer la transcription
    start = requests.post(
        "https://api.replicate.com/v1/predictions",
        json={
            "version": "a53f6b6e2fdf5c8588465244cd8140e567d0ffb55d0b8042c8c73c0fdf854122",
            "input": {"audio": file_url}
        },
        headers=headers
    )
    prediction = start.json()
    get_url = prediction.get("urls", {}).get("get")

    # Polling jusqu'à succès
    for _ in range(30):
        poll = requests.get(get_url, headers=headers).json()
        if poll["status"] == "succeeded":
            return poll["output"]
        elif poll["status"] == "failed":
            raise Exception("Transcription échouée.")
        time.sleep(2)

    raise Exception("Timeout transcription")

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
        transcription = transcribe_with_replicate(audio_bytes)
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
            "message": "Transcription réussie",
            "transcription": transcription,
            "summary": summary,
            "tasks": tasks
        }

    except Exception as e:
        print("❌ ERREUR PROCESS SUMMARY:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Erreur traitement transcription")
