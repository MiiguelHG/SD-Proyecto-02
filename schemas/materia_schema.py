from pydantic import BaseModel

class Materia(BaseModel):
    nombre: str
    descripcion: str