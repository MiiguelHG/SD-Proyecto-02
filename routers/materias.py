from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId

from ..db.db import db
from ..schemas.materia_schema import Materia
from ..config.dependencies import get_current_active_user

materia_collection = db["materias"]
profesor_materia_collection = db["profesores_materias"]
alumno_materia_collection = db["alumnos_materias"]

router = APIRouter(
    prefix="/materia",
    tags=["Materia"],
    dependencies=[Depends(get_current_active_user)]
)

async def obtener_materia(id: str):
    try:
        materia = await materia_collection.find_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error materia: {str(e)}")
    
    if materia:
        materia["_id"] = str(materia["_id"])
        return materia
    raise HTTPException(status_code=404, detail="Materia no encontrada")

@router.post("/", response_description="Agregar una materia", status_code=201)
async def save_materia(materia: Materia):
    try:
        result = await materia_collection.insert_one(materia.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error save materia: {str(e)}")
    
    if result.acknowledged:
        # Return 201 Created status code y el ID de la materia creada
        new_materia = await obtener_materia(str(result.inserted_id))
        if new_materia:
            new_materia["_id"] = str(new_materia["_id"])
            return new_materia
        
    raise HTTPException(status_code=404, detail="Materia no creada")

@router.get("/", response_description="Obtener todas las materias")
async def get_all_materias():
    materias_list = []
    try:
        materias = await materia_collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error get all materias: {str(e)}")
    
    for materia in materias:
        materia["_id"] = str(materia["_id"])
        materias_list.append(materia)
    return materias_list

@router.get("/{id}", response_description="Obtener una materia por su ID")
async def get_materia_by_id(id: str):
    return await obtener_materia(id)

@router.put("/{id}", response_description="Actualizar una materia por su ID")
async def update_materia_by_id(id: str, materia: Materia):
    try:
        result = await materia_collection.update_one({"_id": ObjectId(id)}, {"$set": materia.dict()})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error update materia: {str(e)}")
    
    if result.modified_count == 1:
        return await obtener_materia(id)
    
    raise HTTPException(status_code=404, detail="Materia no actualizada")

@router.delete("/{id}", response_description="Eliminar una materia por su ID")
async def delete_materia_by_id(id: str):
    try:
        result = await materia_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error delete materia: {str(e)}")
    
    if result.deleted_count == 1:
        # Buscar si la materia esta en el listado de materias de un profesor y eliminarla
        try:
            result_prfesor = await profesor_materia_collection.update_many(
                {"materias": ObjectId(id)},
                {"$pull": {"materias": ObjectId(id)}}
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error delete materia profesor: {str(e)}")
        
        # comprobar si la consulta fue exitosa
        if not result_prfesor.acknowledged:
            raise HTTPException(status_code=400, detail="Error al eliminar materia de profesor")
        
        # Eliminar la materia de alumnos_materias 
        try:
            result_alumno = await alumno_materia_collection.delete_many({"materia_id": ObjectId(id)})
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error delete materia alumno: {str(e)}")
        
        # comprobar si la consulta fue exitosa
        if not result_alumno.acknowledged:
            raise HTTPException(status_code=400, detail="Error al eliminar materia de alumnos")

        return {"message": "Materia eliminada"}
    
    raise HTTPException(status_code=404, detail="Materia no eliminada")