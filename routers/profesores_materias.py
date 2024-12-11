from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId

from ..db.db import db
from ..schemas.profesor_schema import AddProfesorMateria
from .profesor import obtener_profesor
from .materias import obtener_materia
from ..config.dependencies import get_current_active_user

profesor_materia_collection = db["profesores_materias"]

router = APIRouter(
    prefix="/profesor_materia",
    tags=["Profesor Materia"],
    dependencies=[Depends(get_current_active_user)]
)

async def obtener_profesor_materia(profesor_id: str):
    try:
        profesor_materia = await profesor_materia_collection.find_one({"profesor_id": ObjectId(profesor_id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error profesor materia: {str(e)}")
    
    if profesor_materia:
        profesor = await obtener_profesor(profesor_id)
        profesor["_id"] = str(profesor["_id"])
        materias = []
        for materia_id in profesor_materia["materias"]:
            try:
                materia = await obtener_materia(str(materia_id))
                materias.append(materia)
            except HTTPException as e:
                # Manejar el error según sea necesario, por ejemplo, omitir la materia
                continue
        profesor["materias"] = materias
        return profesor

    raise HTTPException(status_code=404, detail="Profesor materia no encontrado")

# Verificar si la materia ya fue agregada a un profesor
async def verificar_materia_profesor(materia_id: str):
    try:
        profesores_materias_db = await profesor_materia_collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error verificar materia profesor: {str(e)}")
    
    for profesor_materia in profesores_materias_db:
        if ObjectId(materia_id) in profesor_materia["materias"]:
            raise HTTPException(status_code=400, detail="Materia ya asignada a un profesor")
    

@router.put("/{profesor_id}", description="Asignar materias a profesores")
async def add_materia_profesor(profesor_id: str, materia: AddProfesorMateria):
    # Verificar si la materia ya fue asignada a un profesor
    await verificar_materia_profesor(materia.materia_id)

    # Asignar materia al profesor
    try:
        result = await profesor_materia_collection.update_one(
            {"profesor_id": ObjectId(profesor_id)},
            {"$addToSet": {"materias": ObjectId(materia.materia_id)}}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error asignar materia profesor: {str(e)}")
    
    if result.modified_count == 1:
        return await obtener_profesor_materia(profesor_id)
    elif result.matched_count == 1:
        raise HTTPException(status_code=404, detail="Materia ya asignada al profesor anteriormente")
    raise HTTPException(status_code=404, detail="Profesor no encontrado")

@router.get("/{profesor_id}", description="Obtener materias de un profesor")
async def get_profesor_materia_by_id(profesor_id: str):
    return await obtener_profesor_materia(profesor_id)

@router.get("/", description="Obtener todos los profesores con sus materias")
async def get_all_profesores_materias():
    profesores_materias = []
    async for profesor_materia in profesor_materia_collection.find():
        profesor_id = str(profesor_materia["profesor_id"])
        profesor = await obtener_profesor_materia(profesor_id)
        profesores_materias.append(profesor)
    return profesores_materias