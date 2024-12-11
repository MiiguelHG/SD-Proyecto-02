from pydantic import BaseModel, validator as pydantic_validator
from datetime import datetime

class Alumno(BaseModel):
    nombre: str
    apellido: str
    fecha_nacimiento: datetime
    direccion: str
    foto: str

class MateriaAlumno(BaseModel):
    alumno_id: str
    materia_id: str