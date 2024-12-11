from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId

from ..db.db import db
from ..schemas.profesor_schema import Profesor
from ..config.dependencies import get_current_active_user

profesor_collection = db["profesores"]
profesor_materia_collection = db["profesores_materias"]

router = APIRouter(
    prefix="/profesor",
    tags=["Profesor"],
    dependencies=[Depends(get_current_active_user)]
)

async def obtener_profesor(id: str):
    try:
        profesor = await profesor_collection.find_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error profesor: {str(e)}")
    
    if profesor:
        profesor["_id"] = str(profesor["_id"])
        return profesor
    raise HTTPException(status_code=404, detail="Profesor no encontrado")

@router.post("/", response_description="Agregar un profesor", status_code=201)
async def save_profesor(profesor: Profesor):
    try:
        result = await profesor_collection.insert_one(profesor.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error save profesor: {str(e)}")
    
    if result.acknowledged:
        # Crear un profesor con listado de materias vacío
        try:
            profesor_materiaDB = {
                "profesor_id": result.inserted_id,
                "materias": []
            }
            profesor_materia = await profesor_materia_collection.insert_one(profesor_materiaDB)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error save profesor_materia: {str(e)}")
        # Return 201 Created status code y el ID del profesor creado

        # verificar que el profesor_materia se haya creado
        if not profesor_materia.acknowledged:
            raise HTTPException(status_code=400, detail="Error: profesor_materia no creado")
        return await obtener_profesor(str(result.inserted_id))
        
    raise HTTPException(status_code=404, detail="Profesor no creado")

@router.get("/", response_description="Obtener todos los profesores")
async def get_all_profesores():
    profesores_list = []
    try:
        profesores = await profesor_collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error get all profesores: {str(e)}")
    
    for profesor in profesores:
        profesor["_id"] = str(profesor["_id"])
        profesores_list.append(profesor)
    return profesores_list

@router.get("/{id}", response_description="Obtener un profesor por su ID")
async def get_profesor_by_id(id: str):
    return await obtener_profesor(id)

@router.put("/{id}", response_description="Actualizar un profesor por su ID")
async def update_profesor_by_id(id: str, profesor: Profesor):
    try:
        result = await profesor_collection.update_one({"_id": ObjectId(id)}, {"$set": profesor.dict()})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error update profesor: {str(e)}")
    
    if result.modified_count == 1:
        return await obtener_profesor(id)
    raise HTTPException(status_code=404, detail="Profesor no actualizado")

@router.delete("/{id}", response_description="Eliminar un profesor por su ID")
async def delete_profesor_by_id(id: str):
    # Eliminar al profesor de la tabla profesor_materia primero
    try:
        result = await profesor_materia_collection.delete_one({"profesor_id": id})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error delete profesor_materia: {str(e)}")
    
    if result.deleted_count != 1:
        raise HTTPException(status_code=404, detail="Profesor materia no eliminado")
    
    # Eliminar profesor
    try:
        result = await profesor_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error delete profesor: {str(e)}")
    
    if result.deleted_count == 1:
        return {"message": "Profesor eliminado"}
    raise HTTPException(status_code=404, detail="Profesor no eliminado")
