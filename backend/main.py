import os
from fastapi import FastAPI
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_DB = os.getenv("MONGO_DB")

MONGO_URI = (
    f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}"
    f"@mongodb:27017/"
)

client = MongoClient(MONGO_URI)

db = client[MONGO_DB]

collection = db["eventos"]


@app.get("/")
def home():
    return {
        "mensaje": "FastAPI funcionando"
    }


@app.post("/event")
def guardar_evento(data: dict):

    evento = {
        **data,
        "fecha": datetime.utcnow()
    }

    resultado = collection.insert_one(evento)

    return {
        "ok": True,
        "id": str(resultado.inserted_id)
    }


@app.get("/events")
def obtener_eventos():

    eventos = []

    for evento in collection.find().sort("fecha", -1):

        evento["_id"] = str(evento["_id"])

        eventos.append(evento)

    return eventos