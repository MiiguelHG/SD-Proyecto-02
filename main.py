from fastapi import FastAPI, Depends

from .config import dependencies
from .routers import profesor, materias, alumnos, profesores_materias, alumnos_materias, calificaciones

# app = FastAPI(dependencies= [Depends(get_current_active_user)])
app = FastAPI()

app.include_router(dependencies.router)
app.include_router(profesor.router)
app.include_router(materias.router)
app.include_router(alumnos.router)
app.include_router(profesores_materias.router)
app.include_router(alumnos_materias.router)
app.include_router(calificaciones.router)

@app.get("/", dependencies=[Depends(dependencies.get_current_user)])
async def root():
    return {"message": "Hello World"}