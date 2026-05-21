from pydantic import BaseModel

class Evento_arduino_movimiento(BaseModel):
    robot_id: str
    tipo: str
    evento: str
    nivel: str
    datos : dict
    timestamp: str


