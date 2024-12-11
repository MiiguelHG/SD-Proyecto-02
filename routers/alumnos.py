from fastapi import APIRouter, Depends, HTTPException, File, Form, UploadFile
from bson import ObjectId
from datetime import datetime
import os
import shutil

from ..db.db import db
from ..schemas.alumno_schema import Alumno
from ..config.dependencies import get_current_active_user
from ..config.s3 import subir_objeto, eliminar_objeto

alumno_collection = db["alumnos"]
alumno_materia_collection = db["alumnos_materias"]

router = APIRouter(
    prefix="/alumno",
    tags=["Alumno"],
    dependencies=[Depends(get_current_active_user)]
)

async def obtener_alumno(id: str):
    try:
        alumno = await alumno_collection.find_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error alumno: {str(e)}")
    
    if alumno:
        alumno["_id"] = str(alumno["_id"])
        return alumno
    raise HTTPException(status_code=404, detail="Alumno no encontrado")

# @router.post("/", response_description="Agregar un alumno", status_code=201)
# async def save_alumno(alumno: Alumno):
#     try:
#         result = await alumno_collection.insert_one(alumno.dict())
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error save alumno: {str(e)}")
    
#     if result.acknowledged:
#         # Return 201 Created status code y el ID del alumno creado
#         new_alumno = await obtener_alumno(str(result.inserted_id))
#         if new_alumno:
#             new_alumno["_id"] = str(new_alumno["_id"])
#             return new_alumno
        
#     raise HTTPException(status_code=404, detail="Alumno no creado")

@router.post("/", response_description="Agregar un alumno", status_code=201)
async def save_alumno(nombre: str = Form(...),
                       apellido: str = Form(...), 
                       fecha_nacimiento: datetime = Form(...),
                       direccion: str = Form(...),
                       foto: UploadFile = File(...)):
    try:
        # Guardar el archivo temporalmente
        with open(foto.filename, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
        # Subir la foto al bucket de S3
        imagen_url = subir_objeto(foto.filename, "alumnos")
        # Eliminar el archivo temporal
        os.remove(foto.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error save alumno s3: {str(e)}")
    try:
        alumno = Alumno(nombre=nombre,
                        apellido=apellido,
                        fecha_nacimiento=fecha_nacimiento,
                        direccion=direccion,
                        foto=imagen_url)
        result = await alumno_collection.insert_one(alumno.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error save alumno: {str(e)}")
    
    if result.acknowledged:
        # Return 201 Created status code y el ID del alumno creado
        new_alumno = await obtener_alumno(str(result.inserted_id))
        if new_alumno:
            new_alumno["_id"] = str(new_alumno["_id"])
            return new_alumno

@router.get("/", response_description="Obtener todos los alumnos")
async def get_all_alumnos():
    alumnos_list = []
    try:
        alumnos = await alumno_collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error get all alumnos: {str(e)}")
    
    for alumno in alumnos:
        alumno["_id"] = str(alumno["_id"])
        alumnos_list.append(alumno)
    return alumnos_list

@router.get("/{id}", response_description="Obtener un alumno por su ID")
async def get_alumno_by_id(id: str):
    return await obtener_alumno(id)

# @router.put("/{id}", response_description="Actualizar un alumno por su ID")
# async def update_alumno_by_id(id: str, alumno: Alumno):
#     try:
#         result = await alumno_collection.update_one({"_id": ObjectId(id)}, {"$set": alumno.dict()})
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error update alumno: {str(e)}")
    
#     if result.modified_count == 1:
#         return await obtener_alumno(id)
    
#     raise HTTPException(status_code=404, detail="Alumno no actualizado")

@router.put("/{id}", response_description="Actualizar un alumno por su ID")
async def update_alumno_by_id(id: str, nombre: str = Form(None),
                               apellido: str = Form(None), 
                               fecha_nacimiento: datetime = Form(None),
                               direccion: str = Form(None),
                               foto: UploadFile = File(None)):
    try:
        # Obtener el alumno
        alumno = await obtener_alumno(id)
        if not alumno:
            raise HTTPException(status_code=404, detail="Alumno no encontrado")
        # Si se proporciona una nueva foto
        if foto:
            try:
                # Eliminar la foto anterior del bucket de S3
                url_eliminar = alumno["foto"]
                objeto_eliminar = url_eliminar.split("/")[-1]
                eliminar_objeto(objeto_eliminar, "alumnos")
                # Guardar el archivo temporalmente
                with open(foto.filename, "wb") as buffer:
                    shutil.copyfileobj(foto.file, buffer)
                # Subir la foto al bucket de S3
                imagen_url = subir_objeto(foto.filename, "alumnos")
                # Eliminar el archivo temporal
                os.remove(foto.filename)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error update alumno s3: {str(e)}")
        else:
            imagen_url = alumno["foto"]
        # Actualizar el alumno
        try:
            result = await alumno_collection.update_one({"_id": ObjectId(id)},
                                                        {"$set": {"nombre": nombre if nombre else alumno["nombre"],
                                                                  "apellido": apellido if apellido is not None else alumno["apellido"],
                                                                  "fecha_nacimiento": fecha_nacimiento if fecha_nacimiento is not None else alumno["fecha_nacimiento"],
                                                                  "direccion": direccion if direccion is not None else alumno["direccion"],
                                                                  "foto": imagen_url}})
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error update alumno: {str(e)}")
        
        if result.modified_count == 1:
            return await obtener_alumno(id)
        
        raise HTTPException(status_code=404, detail="Alumno no actualizado")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error update alumno: {str(e)}")

@router.delete("/{id}", response_description="Eliminar un alumno por su ID")
async def delete_alumno_by_id(id: str):
    # Eliminar la foto del bucket de S3
    try:
        # Obtener el alumno
        alumno = await obtener_alumno(id)
        if not alumno:
            raise HTTPException(status_code=404, detail="Alumno no encontrado")
        url_foto = alumno["foto"]
        # Extraer el nombre del archivo (la ultima parte de la URL)
        nombre_objeto = url_foto.split("/")[-1]
        # Eliminar la foto del bucket de S3
        eliminar_objeto(nombre_objeto, "alumnos")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error delete alumno s3: {str(e)}")

    # Eliminar el alumno
    try:
        result = await alumno_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error delete alumno: {str(e)}")
    
    if result.deleted_count == 1:
        # Si el alumno está inscrito en alguna materia, se debe eliminar la relación con la materia
        try:
            await alumno_materia_collection.delete_many({"alumno_id": ObjectId(id)})
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error delete alumno materia: {str(e)}")
        
        return HTTPException(status_code=204, detail="Alumno eliminado exitosamente")
    
    raise HTTPException(status_code=404, detail="Alumno no eliminado")