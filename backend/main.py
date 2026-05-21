import os
from fastapi import FastAPI
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

from models.modelo_evento import Evento_arduino_movimiento as Evento_movimiento

#import para busqueda por ID
from bson import ObjectId



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


#******************Obtner todos los eventos****************
@app.get("/api/v1/eventos")
def obtener_eventos():

    lista_eventos = []

    for eventos in db["eventos"].find():

        eventos["_id"] = str(eventos["_id"])

        lista_eventos.append(eventos)

    return lista_eventos

#******************Obtner eventos con limite de 5****************
@app.get("/api/v1/eventos/recientes")
#mostrar numero de registros reciente (limit)
def obtener_eventos_recientes(limit : int = 5):

    lista_eventos = []

    for eventos in db["eventos"].find().sort("timestamp", -1).limit(limit):

        eventos["_id"] = str(eventos["_id"])

        lista_eventos.append(eventos)

    return lista_eventos


#******************Obtner todos los eventos****************
@app.get("/api/v1/eventos/recientes/limite/{limite}")
#mostrar numero de registros reciente (limit)
def obtener_eventos_recientes(limite: int):

    lista_eventos = []

    for eventos in db["eventos"].find().sort("timestamp", -1).limit(limite):

        eventos["_id"] = str(eventos["_id"])

        lista_eventos.append(eventos)

    return lista_eventos


#****************Obtener evento por ID************************


@app.get("/api/v1/eventos/{id}")
def obtener_evento(id: str):

    try:
        evento = db["eventos"].find_one({
        "_id": ObjectId(id)
        })

        if not evento:
            return {
            "error": "Evento no encontrado"
            }

        evento["_id"] = str(evento["_id"])

        return evento
    except:
        return{"error":"ID invalido"}


#****************Registrar evento************************

@app.post("/api/v1/eventos")

def registro_evento(evento_arduino: Evento_movimiento):

    #formato de hora
    hora = datetime.now()
    formato = hora.strftime("%d/%m/%Y %I:%M:%S %p")

    nuevo_evento = {
        "robot_id": evento_arduino.robot_id,
        "tipo": evento_arduino.tipo,
        "evento": evento_arduino.evento,
        "nivel": evento_arduino.nivel,
        "datos": evento_arduino.datos,
        "timestamp": formato
    }

    resultado = db["eventos"].insert_one(nuevo_evento)

    return {
        "mensaje": "Evento registrado",
        "id": str(resultado.inserted_id)
    }



#***************endpoint health solo backend********************
@app.get("/api/v1/health")
def health():
    return {"status": "online"}

#***************endpoint estado MongoDB********************
@app.get("/api/v1/status")
def estado_db():

    try:

        # comando ping a MongoDB
        client.admin.command("ping")

        return {
            "status": "online",
            "database": MONGO_DB,
            "mongo": "conectado"
        }

    except Exception as e:

        return {
            "status": "offline",
            "error": str(e)
        }