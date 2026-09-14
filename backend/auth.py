# ============================================
#  SISTEMA DE AUTENTICACIÓN
#  Contraseñas + JWT Tokens
# ============================================

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict

from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from utils import Utils

# ============================================
#  CONFIGURACIÓN
# ============================================

# Clave secreta para firmar tokens (CAMBIAR en producción)
SECRET_KEY = os.getenv("SECRET_KEY", "cambiar_esta_clave_en_produccion_astro_ia")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

# Contexto de hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema HTTP Bearer
security = HTTPBearer(auto_error=False)


# ============================================
#  FUNCIONES DE HASH
# ============================================


def hash_password(password: str) -> str:
    """Hashea una contraseña"""
    return pwd_context.hash(password)


def verificar_password(password: str, hashed: str) -> bool:
    """Verifica que una contraseña coincida con su hash"""
    try:
        return pwd_context.verify(password, hashed)
    except Exception:
        return False


# ============================================
#  FUNCIONES JWT
# ============================================


def crear_token(usuario_id: str, nombre: str) -> str:
    """Crea un token JWT para un usuario"""
    expiracion = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": usuario_id,
        "nombre": nombre,
        "exp": expiracion,
        "iat": datetime.utcnow(),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(token: str) -> Optional[Dict]:
    """Verifica un token JWT y devuelve el payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ============================================
#  GESTOR DE USUARIOS
# ============================================


class AuthManager:
    def __init__(self, directorio: str = "conocimiento/"):
        self.directorio = directorio
        self.archivo_usuarios = f"{directorio}usuarios_auth.json"
        self._crear_directorio()
        self.usuarios = self._cargar_usuarios()

    def _crear_directorio(self):
        os.makedirs(self.directorio, exist_ok=True)

    def _cargar_usuarios(self) -> Dict:
        """Carga la base de datos de usuarios"""
        if os.path.exists(self.archivo_usuarios):
            try:
                return Utils.cargar_json(self.archivo_usuarios)
            except:
                return {"usuarios": {}}
        return {"usuarios": {}}

    def _guardar_usuarios(self):
        """Guarda la base de datos de usuarios"""
        Utils.guardar_json(self.usuarios, self.archivo_usuarios)

    def registrar(self, nombre: str, password: str) -> Dict:
        """
        Registra un nuevo usuario.

        Returns:
            {
                "exito": True,
                "usuario_id": "jesus_abc123",
                "nombre": "jesus",
                "token": "eyJhbGc...",
                "mensaje": "Usuario registrado correctamente"
            }
        """
        # Validaciones
        if not nombre or len(nombre) < 3:
            return {
                "exito": False,
                "error": "El nombre debe tener al menos 3 caracteres",
            }

        if not password or len(password) < 6:
            return {
                "exito": False,
                "error": "La contraseña debe tener al menos 6 caracteres",
            }

        # Normalizar nombre
        nombre_normalizado = nombre.lower().strip()

        # Verificar si ya existe
        if nombre_normalizado in self.usuarios["usuarios"]:
            return {"exito": False, "error": "El usuario ya existe"}

        # Crear usuario
        usuario_id = f"{nombre_normalizado}_{str(uuid.uuid4())[:8]}"

        usuario = {
            "usuario_id": usuario_id,
            "nombre": nombre_normalizado,
            "nombre_original": nombre.strip(),
            "password_hash": hash_password(password),
            "creado": datetime.now().isoformat(),
            "ultimo_login": datetime.now().isoformat(),
            "activo": True,
        }

        self.usuarios["usuarios"][nombre_normalizado] = usuario
        self._guardar_usuarios()

        # Crear token
        token = crear_token(usuario_id, nombre_normalizado)

        return {
            "exito": True,
            "usuario_id": usuario_id,
            "nombre": nombre_normalizado,
            "nombre_original": nombre.strip(),
            "token": token,
            "mensaje": "Usuario registrado correctamente",
        }

    def login(self, nombre: str, password: str) -> Dict:
        """
        Inicia sesión con un usuario existente.

        Returns:
            {
                "exito": True,
                "usuario_id": "...",
                "nombre": "...",
                "token": "...",
                "mensaje": "Sesión iniciada"
            }
        """
        nombre_normalizado = nombre.lower().strip()

        # Buscar usuario
        if nombre_normalizado not in self.usuarios["usuarios"]:
            return {"exito": False, "error": "Usuario o contraseña incorrectos"}

        usuario = self.usuarios["usuarios"][nombre_normalizado]

        # Verificar contraseña
        if not verificar_password(password, usuario["password_hash"]):
            return {"exito": False, "error": "Usuario o contraseña incorrectos"}

        # Verificar que esté activo
        if not usuario.get("activo", True):
            return {"exito": False, "error": "Usuario desactivado"}

        # Actualizar último login
        usuario["ultimo_login"] = datetime.now().isoformat()
        self._guardar_usuarios()

        # Crear token
        token = crear_token(usuario["usuario_id"], nombre_normalizado)

        return {
            "exito": True,
            "usuario_id": usuario["usuario_id"],
            "nombre": nombre_normalizado,
            "nombre_original": usuario.get("nombre_original", nombre_normalizado),
            "token": token,
            "mensaje": "Sesión iniciada correctamente",
        }

    def verificar_sesion(self, token: str) -> Optional[Dict]:
        """Verifica un token y devuelve el usuario"""
        payload = verificar_token(token)
        if not payload:
            return None

        nombre = payload.get("nombre")
        if not nombre or nombre not in self.usuarios["usuarios"]:
            return None

        usuario = self.usuarios["usuarios"][nombre]

        return {
            "usuario_id": usuario["usuario_id"],
            "nombre": usuario["nombre"],
            "nombre_original": usuario.get("nombre_original", usuario["nombre"]),
        }

    def cambiar_password(
        self, nombre: str, password_actual: str, password_nueva: str
    ) -> Dict:
        """Cambia la contraseña de un usuario"""
        nombre_normalizado = nombre.lower().strip()

        if nombre_normalizado not in self.usuarios["usuarios"]:
            return {"exito": False, "error": "Usuario no encontrado"}

        usuario = self.usuarios["usuarios"][nombre_normalizado]

        # Verificar contraseña actual
        if not verificar_password(password_actual, usuario["password_hash"]):
            return {"exito": False, "error": "Contraseña actual incorrecta"}

        # Validar nueva
        if len(password_nueva) < 6:
            return {
                "exito": False,
                "error": "La nueva contraseña debe tener al menos 6 caracteres",
            }

        # Actualizar
        usuario["password_hash"] = hash_password(password_nueva)
        self._guardar_usuarios()

        return {"exito": True, "mensaje": "Contraseña actualizada"}

    def listar_usuarios_publicos(self) -> list:
        """
        Lista usuarios SIN información sensible.
        Solo nombre para mostrar en el selector (opcional).
        """
        return [
            {
                "nombre": u["nombre"],
                "nombre_original": u.get("nombre_original", u["nombre"]),
            }
            for u in self.usuarios["usuarios"].values()
            if u.get("activo", True)
        ]


# ============================================
#  DEPENDENCIA PARA FASTAPI
# ============================================


async def obtener_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict:
    """
    Dependencia que verifica el token JWT.
    Se usa en endpoints protegidos.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = verificar_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "usuario_id": payload.get("sub"),
        "nombre": payload.get("nombre"),
    }
