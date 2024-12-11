from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId

class Profesor(BaseModel):
    nombre: str
    apellido: str
    fecha_nacimiento: datetime
    direccion: str
    especialidad: str

class AddProfesorMateria(BaseModel):
    materia_id: str
    