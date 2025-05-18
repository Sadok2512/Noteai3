from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import os

import app.auth as auth
import app.transcribe as transcribe
import app.auth_verify as auth_verify
import app.auth_google as auth_google
import app.history as history
import app.upload_audio as upload_audio
import app.process_summary as process_summary

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["noteai"]

app = FastAPI(title="NoteAI Backend")

# TEMP: Autoriser toutes les origines pour débogage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ autorise tout pour test
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/auth")
app.include_router(transcribe.router)
app.include_router(auth_verify.router)
app.include_router(auth_google.router, prefix="/auth")
app.include_router(history.router)
app.include_router(upload_audio.router)
app.include_router(process_summary.router)

@app.get("/")
def root():
    return {"message": "NoteAI backend is running."}
