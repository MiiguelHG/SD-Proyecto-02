from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId

from ..db.db import db
from ..schemas.calificacion_schema import Calificacion
from .alumnos import obtener_alumno
from .materias import obtener_materia
from ..config.dependencies import get_current_active_user

alumno_materia_collection = db["alumnos_materias"]

router = APIRouter(
    prefix="/calificaciones",
    tags=["Calificaciones"],
    dependencies=[Depends(get_current_active_user)]
)

async def obtener_calificaciones_alumno(alumno_id: str):
    try:
        alumno_calificaciones = await alumno_materia_collection.find({"alumno_id": ObjectId(alumno_id)}).to_list(None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error calificaciones alumno: {str(e)}")
    
    calificaciones_list = []
    alumno = await obtener_alumno(alumno_id)
    alumno["_id"] = str(alumno["_id"])

    # Iterar sobre las materias registradas para el alumno
    for calificacion in alumno_calificaciones:
        # Verificar si el alumno tiene calificaciones
        if "calificacion" not in calificacion or calificacion["calificacion"] is None:
            continue
        materia = await obtener_materia(str(calificacion["materia_id"]))
        materia["_id"] = str(materia["_id"])
        calificacion_dict = dict()
        calificacion_dict["calificacion"] = calificacion["calificacion"]
        calificacion_dict["materia"] = materia
        calificaciones_list.append(calificacion_dict)
    
    alumno["calificaciones"] = calificaciones_list
    return alumno
     

@router.put("/{alumno_id}/materia/{materia_id}", response_description="Agragar calificación de un alumno en una materia")
async def add_calificacion(alumno_id: str, materia_id: str, calificacion: Calificacion):
    try:
        result = await alumno_materia_collection.update_one(
            {"alumno_id": ObjectId(alumno_id), "materia_id": ObjectId(materia_id)},
            {"$set": {"calificacion": calificacion.calificacion}}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error save calificacion: {str(e)}")
    
    if result.modified_count == 1:
        return await obtener_calificaciones_alumno(alumno_id)
    
    raise HTTPException(status_code=404, detail="Calificación no guardada")

@router.get("/{alumno_id}", response_description="Obtener todas las calificaciones de un alumno")
async def get_all_calificaciones_alumno(alumno_id: str):
    return await obtener_calificaciones_alumno(alumno_id)

@router.get("/", response_description="Obtener todos los alumnos con sus calificaciones")
async def get_all_calificaciones():
    alumnos_calificaciones = []
    try:
        alumnos = await alumno_materia_collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error get all calificaciones: {str(e)}")
    
    for alumno in alumnos:
        alumno_id = str(alumno["alumno_id"])
        calificaciones = await obtener_calificaciones_alumno(alumno_id)
        alumnos_calificaciones.append(calificaciones)
    return alumnos_calificaciones