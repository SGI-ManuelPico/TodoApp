Título: Aplicación para manejar tareas.

Estructura:

    /.venv/ 

    Es el virtual environment del proyecto.

    /app/

    1. core → En esta se encuentran la lógica de conexión a la base de datos, autorización y seguridad.
    2. models → Clases del ORM para abstraer la estructura de la base de datos.
    3. routes → Puntos de acceso, estas son las rutas que consume el frontend.
    4. schemas → Acá definimos los tipos de estrucuturas que queremeos recibir o mandar al usuario.
    5. crud → Operacionea CRUD sobre los modelos.
    6. main.py → Acá agrupamos todas las rutas para inicializar la API.

    /migrations/

    La carpeta migrations la genera automáticamente Alembic cuando se hace la primera migración. Ahí se van guardando todas las migraciones 
    que se hagan como resultado de alterar los modelos. Cada migración tiene un id asociado, que se puede encontrar en una tabla que se genera
    en la base de datos para poder saber en cual versión de la base de datos nos encontramos. 


    Requerimientos:

    Python 3.12.5 64 bit (Ya viene en el venv)

    Librerias
    - FastAPI, Alembic, Pydantic, SQLAlchemy, ...

