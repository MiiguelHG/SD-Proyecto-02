# Sistema de Gestión de Información Escolar UPIIZ

Este proyecto implementa una API RESTful para la gestión de información de estudiantes, profesores y materias de la UPIIZ.  Utiliza FastAPI como framework, MongoDB como base de datos y AWS S3 para el almacenamiento de fotos de los alumnos.

## Funcionalidades

La API proporciona las siguientes funcionalidades:

**Alumnos:**

* **Crear:** Permite crear nuevos registros de alumnos con información como nombre, apellido, fecha de nacimiento, dirección y foto. La foto se sube a un bucket de S3 y la URL se almacena en la base de datos.
* **Leer:** Permite obtener la información de todos los alumnos o de un alumno específico mediante su ID.
* **Actualizar:** Permite modificar la información de un alumno existente, incluyendo la posibilidad de cambiar su foto. Si se proporciona una nueva foto, la anterior se elimina de S3.
* **Eliminar:** Elimina un alumno de la base de datos. Al eliminar un alumno, también se borra su foto de S3 y las relaciones que tiene con las materias a las que esta inscrito.

**Profesores:**

* **Crear:** Permite crear nuevos registros de profesores con información como nombre, apellido, fecha de nacimiento, dirección y especialidad. Al crear un profesor, también se crea un registro en la colección `profesores_materias` con un array vacío para las materias que se le asignarán posteriormente.
* **Leer:** Permite obtener la información de todos los profesores o de un profesor específico mediante su ID.
* **Actualizar:** Permite modificar la información de un profesor existente.
* **Eliminar:** Elimina un profesor de la base de datos. Al eliminar un profesor, también se elimina su registro de la colección `profesores_materias`.

**Materias:**

* **Crear:** Permite crear nuevos registros de materias con nombre y descripción.
* **Leer:** Permite obtener la información de todas las materias o de una materia específica mediante su ID.
* **Actualizar:** Permite modificar la información de una materia existente.
* **Eliminar:** Elimina una materia de la base de datos. Al eliminar una materia, también se elimina de las listas de materias de los profesores que la imparten y de la colección `alumnos_materias`.

**Asignación de Materias a Profesores:**

* Permite asignar una o varias materias a un profesor.
* Un profesor puede tener varias materias asignadas.
* Se verifica que la materia no esté ya asignada a otro profesor antes de realizar la asignación.

**Inscripción de Alumnos a Materias:**

* Permite inscribir a un alumno en una o varias materias.
* Un alumno puede estar inscrito en varias materias.

**Calificaciones:**

* Permite registrar la calificación de un alumno en una materia específica.
* Las calificaciones se almacenan en la colección `alumnos_materias` junto con la información de la materia y el alumno.
* Se valida que la calificación esté entre 0 y 10.

**Autenticación y Autorización:**

* Implementa autenticación mediante OAuth2 con tokens JWT.
* Se utiliza un endpoint `/token` para obtener el token de acceso.
* Las rutas protegidas requieren un token de acceso válido.
* Se verifica si el usuario está deshabilitado antes de permitir el acceso.

**Validación de Datos:**

* Se utiliza Pydantic para validar los datos de entrada y asegurar que sean correctos y consistentes.


## Estructura del Proyecto

El proyecto está organizado en las siguientes carpetas:

* **`config`:** Contiene la configuración de la aplicación, incluyendo las dependencias de FastAPI y la conexión a S3.
* **`db`:** Contiene la configuración de la conexión a la base de datos MongoDB.
* **`routers`:** Contiene los routers de la API, que definen las rutas y las funciones para cada entidad (alumnos, profesores, materias, etc.).
* **`schemas`:** Contiene los esquemas de Pydantic, que definen la estructura de los datos de entrada y salida.

## Documentación

La API está documentada con Swagger UI, accesible en la ruta `/docs`. La documentación proporciona información detallada sobre cada endpoint, incluyendo los parámetros de entrada, los códigos de respuesta y ejemplos de uso.

## Despliegue


## Tecnologías Utilizadas

* **FastAPI:** Framework web de alto rendimiento para construir APIs con Python.
* **MongoDB:** Base de datos NoSQL orientada a documentos.
* **AWS S3:** Servicio de almacenamiento de objetos en la nube.
* **Pydantic:** Librería para la validación de datos y la creación de modelos de datos.
* **Motor:**  Librería para interactuar con MongoDB de forma asíncrona.
* **Boto3:**  SDK de AWS para Python.
* **JWT (JSON Web Token):** Estándar para la creación de tokens de acceso.
* **OAuth2:** Framework de autorización.