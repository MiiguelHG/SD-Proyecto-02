from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import InvalidTokenError

from ..schemas.userSchema import User, UserInDB, Token, TokenData
from ..db.db import db

ACCESS_TOKEN_EXPIRE_MINUTES = 20
ALGORITHM = "HS256"
SECRET_KEY = "ud4mtop8bdvd68261ndpt1cl3jhc9iy54d7uthd0dujnudpx1cf16a2kafvost8w"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

user_collection = db["usuarios"]

router = APIRouter()

# Verificar la contraseña
def verify_password(plain_password, password):
    return plain_password == password

# Obtener un usuario por su nombre de usuario
async def get_user(username: str):
    try:
        user = await user_collection.find_one({"username": username})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al buscar usuario: {str(e)}")
    
    if user:
        del user["_id"]
        return UserInDB(**user)
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

# Autenticar un usuario
async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

# Crear un token de acceso
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Obtener el usuario actual
async def get_current_user(token: str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pueden validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    
    usuario = await get_user(username=token_data.username)
    if usuario is None:
        raise credentials_exception
    return usuario

# Verificar si el usuario esta deshabilitado
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Usuario deshabilitado")
    return current_user

# Iniciar sesión para obtener un token de acceso
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
             detail="Usuario o contraseña incorrectos",
             headers={"WWW-Authenticate": "Bearer"}
             )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username
            },
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")