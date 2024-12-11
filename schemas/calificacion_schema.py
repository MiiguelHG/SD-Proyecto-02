from pydantic import BaseModel, validator as pydantic_validator

class Calificacion(BaseModel):
    calificacion: float | None = None
    class Config:
        json_schema_extra = {
            "example": {
                "calificacion": 9.5
            }
        }

    @pydantic_validator('calificacion')
    def calificacion_range(cls, value):
        if value < 0 or value > 10:
            raise ValueError('La calificación debe estar entre 0 y 10')
        return value