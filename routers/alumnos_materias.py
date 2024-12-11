from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId

from ..db.db import db
from ..schemas.alumno_schema import MateriaAlumno
from .alumnos import obtener_alumno
from .materias import obtener_materia
from ..config.dependencies import get_current_active_user

alumno_materia_collection = db["alumnos_materias"]

router = APIRouter(
    prefix="/materia_alumno",
    tags=["Inscripcion de Alumno a Materia"],
    # dependencies=[Depends(get_current_active_user)]
)

async def obtener_materia_alumnos(materia_id: str):
    try:
        materia_alumnos = await alumno_materia_collection.find({"materia_id": ObjectId(materia_id)}).to_list(None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error materia alumnos: {str(e)}")
    
    alumnos = []

    for materia_alumno in materia_alumnos:
        alumno = await obtener_alumno(str(materia_alumno["alumno_id"]))
        alumno["_id"] = str(alumno["_id"])
        alumnos.append(alumno)

    materia = await obtener_materia(materia_id)
    materia["_id"] = str(materia["_id"])
    materia["alumnos"] = alumnos
    return materia

@router.post("/", response_description="Inscribir un alumno a una materia", status_code=201)
async def save_alumno_materia(materia_alumno: MateriaAlumno):
    try:
        materia_id = ObjectId(materia_alumno.materia_id)
        alumno_id = ObjectId(materia_alumno.alumno_id)
        materia_alumno_dict = dict(materia_id=materia_id, alumno_id=alumno_id)
        result = await alumno_materia_collection.insert_one(materia_alumno_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error save alumno materia: {str(e)}")
    
    if result.acknowledged:
        return await obtener_materia_alumnos(materia_alumno.materia_id)
    
    raise HTTPException(status_code=404, detail="Alumno materia no creado")

@router.get("/{materia_id}", response_description="Obtener todos los alumnos de una materia")
async def get_all_alumnos_materia(materia_id: str):
    return await obtener_materia_alumnos(materia_id)

@router.get("/", response_description="Obtener todas las materias con sus alumnos")
async def get_all_materias_alumnos():
    materias = []
    try:
        materias_db = await alumno_materia_collection.distinct("materia_id")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error get all materias alumnos: {str(e)}")
    
    for materia_id in materias_db:
        materias.append(await obtener_materia_alumnos(str(materia_id)))
    return materias


# @router.delete("/{materia_id}/{alumno_id}", response_description="Eliminar un alumno de una materia")
# async def delete_alumno_materia(materia_id: str, alumno_id: str):
#     try:
#         result = await alumno_materia_collection.delete_one({"materia_id": ObjectId(materia_id), "alumno_id": ObjectId(alumno_id)})
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error delete alumno materia: {str(e)}")
    
#     if result.deleted_count:
#         return await obtener_materia_alumnos(materia_id)
    
#     raise HTTPException(status_code=404, detail="Alumno materia no encontrado")

# @router.put("/")
# async def update_alumno_materia(materia_alumno: MateriaAlumno):
#     try:
#         result = await alumno_materia_collection.update_one(
#             {"materia_id": ObjectId(materia_alumno.materia_id), "alumno_id": ObjectId(materia_alumno.alumno_id)},
#             {"$set": {"materia_id": ObjectId(materia_alumno.materia_id), "alumno_id": ObjectId(materia_alumno.alumno_id)}}
#         )
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error update alumno materia: {str(e)}")
    
#     if result.modified_count:
#         return await obtener_materia_alumnos(materia_alumno.materia_id)
    
#     raise HTTPException(status_code=404, detail="Alumno materia no actualizado")