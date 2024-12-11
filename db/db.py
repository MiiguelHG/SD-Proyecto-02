# Conexion con MongoDB
from motor import motor_asyncio

# URI de la base de datos en Atlas MongoDB
MONGO_URI = "mongodb+srv://root:mFgmRxhF8X0H8Xq9@db-sistemas-distribuido.zwarr.mongodb.net/?retryWrites=true&w=majority&appName=db-sistemas-distribuidos"

# Ejecutar el cliente de la base de datos
client = motor_asyncio.AsyncIOMotorClient(MONGO_URI)

# Seleccionar la base de datos
db = client["proyecto2"]