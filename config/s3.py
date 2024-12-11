import boto3
from botocore.exceptions import NoCredentialsError
import os

# Definir el servicio y la regin de AWS
session = boto3.Session(profile_name="miguel")
s3 = session.client("s3", region_name="us-east-2")

bucket = "proyecto2-upiiz-sistemas-distribuidos-miguel"

# Subir imagenes a una subcarpeta en el bucket
def subir_objeto(archivo, carpeta, bucket=bucket, nombre_objeto=None):
    if nombre_objeto is None:
        nombre_objeto = os.path.basename(archivo)

    # Incluir la carpeta en el nombre del objeto
    nombre_objeto = f"{carpeta}/{nombre_objeto}"

    # Subir el archivo al bucket
    try:
        s3.upload_file(archivo, bucket, nombre_objeto)

        # Generar la URL del objeto
        url = f"https://{bucket}.s3.us-east-2.amazonaws.com/{nombre_objeto}"
        # url2 = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': nombre_objeto})
        print("El archivo se subio correctamente!")
        return url
    except FileNotFoundError:
        # Verifica que el archivo exista localmente
        print("El archivo no existe")
    except NoCredentialsError:
        # Verifica que tengamos credenciales de AWS
        print("Las credenciales de AWS no se encontraron")

# Eliminar un objeto del bucket
def eliminar_objeto(nombre_objeto,carpeta, bucket=bucket):
    try:
        # Eliminar el objeto del bucket
        s3.delete_object(Bucket=bucket, Key=f"{carpeta}/{nombre_objeto}")
        print("El archivo se eliminó correctamente!")
    except NoCredentialsError:
        # Verifica que tengamos credenciales de AWS
        print("Las credenciales de AWS no se encontraron")
    except Exception as e:
        print(f"Error al eliminar el archivo: {e}")

        