# ============================================
#  SISTEMA DE AUTENTICACIÓN
#  Email + Password + JWT Tokens
# ============================================

import os
import re
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

SECRET_KEY = os.getenv("SECRET_KEY", "cambiar_esta_clave_en_produccion_astro_ia")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

# Regex para validar email
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


# ============================================
#  UTILIDADES
# ============================================


def validar_email(email: str) -> bool:
    """Valida el formato de un email"""
    return bool(EMAIL_REGEX.match(email))


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verificar_password(password: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(password, hashed)
    except Exception:
        return False


def crear_token(usuario_id: str, nombre: str, email: str = "") -> str:
    """Crea un token JWT"""
    expiracion = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": usuario_id,
        "nombre": nombre,
        "email": email,
        "exp": expiracion,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(token: str) -> Optional[Dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
        if os.path.exists(self.archivo_usuarios):
            try:
                return Utils.cargar_json(self.archivo_usuarios)
            except:
                return {"usuarios": {}, "emails": {}}
        return {"usuarios": {}, "emails": {}}

    def _guardar_usuarios(self):
        Utils.guardar_json(self.usuarios, self.archivo_usuarios)

    # ==========================================
    #  REGISTRO
    # ==========================================

    def registrar(self, nombre: str, 
                  email: str, 
                  password: str, 
                  acepta_politicas: bool = True) -> Dict:
        """
        Registra un nuevo usuario con nombre, email y contraseña.
        """
        # Validaciones
        if not nombre or len(nombre) < 3:
            return {
                "exito": False,
                "error": "El nombre debe tener al menos 3 caracteres",
            }

        if not email or not validar_email(email):
            return {"exito": False, "error": "El email no es válido"}

        if not password or len(password) < 6:
            return {
                "exito": False,
                "error": "La contraseña debe tener al menos 6 caracteres",
            }

        if not acepta_politicas:
            return {"exito": False, 
                    "error": "Debes aceptar las políticas de privacidad"}

        # Normalizar
        nombre_normalizado = nombre.lower().strip()
        email_normalizado = email.lower().strip()

        # Asegurar estructura
        if "emails" not in self.usuarios:
            self.usuarios["emails"] = {}

        # Verificar nombre duplicado
        if nombre_normalizado in self.usuarios["usuarios"]:
            return {"exito": False, "error": "El nombre de usuario ya está en uso"}

        # Verificar email duplicado
        if email_normalizado in self.usuarios["emails"]:
            return {"exito": False, "error": "El email ya está registrado"}

        # Crear usuario
        usuario_id = f"{nombre_normalizado}_{str(uuid.uuid4())[:8]}"

        usuario = {
            "usuario_id": usuario_id,
            "nombre": nombre_normalizado,
            "nombre_original": nombre.strip(),
            "email": email_normalizado,
            "password_hash": hash_password(password),
            "creado": datetime.now().isoformat(),
            "ultimo_login": datetime.now().isoformat(),
            "activo": True,
            "metodo_registro": "email",
            "politicas": {
                "aceptadas": True,
                "version": "1.0.0",
                "fecha_aceptacion": datetime.now().isoformat(),
                "ip": None,  # Se puede añadir la IP si se desea
            }
        }

        # Guardar en ambos índices
        self.usuarios["usuarios"][nombre_normalizado] = usuario
        self.usuarios["emails"][email_normalizado] = nombre_normalizado
        self._guardar_usuarios()

        # Crear token
        token = crear_token(usuario_id, nombre_normalizado, email_normalizado)

        return {
            "exito": True,
            "usuario_id": usuario_id,
            "nombre": nombre_normalizado,
            "nombre_original": nombre.strip(),
            "email": email_normalizado,
            "token": token,
            "mensaje": "Usuario registrado correctamente",
        }

    # ==========================================
    #  LOGIN (con nombre o email)
    # ==========================================

    def login(self, identificador: str, password: str) -> Dict:
        """
        Inicia sesión con nombre de usuario O email.

        Args:
            identificador: Puede ser el nombre de usuario o el email
            password: La contraseña
        """
        if not identificador:
            return {"exito": False, "error": "Usuario o email requerido"}

        identificador = identificador.lower().strip()

        # Determinar si es email o nombre
        if "@" in identificador:
            # Es email
            if "emails" not in self.usuarios:
                self.usuarios["emails"] = {}

            if identificador not in self.usuarios["emails"]:
                return {"exito": False, "error": "Email o contraseña incorrectos"}

            nombre = self.usuarios["emails"][identificador]
        else:
            # Es nombre de usuario
            nombre = identificador

        # Buscar usuario
        if nombre not in self.usuarios["usuarios"]:
            return {"exito": False, "error": "Usuario o contraseña incorrectos"}

        usuario = self.usuarios["usuarios"][nombre]

        # Verificar contraseña
        if not verificar_password(password, usuario["password_hash"]):
            return {"exito": False, "error": "Usuario o contraseña incorrectos"}

        # Verificar activo
        if not usuario.get("activo", True):
            return {"exito": False, "error": "Usuario desactivado"}

        # Actualizar último login
        usuario["ultimo_login"] = datetime.now().isoformat()
        self._guardar_usuarios()

        # Crear token
        token = crear_token(
            usuario["usuario_id"], usuario["nombre"], usuario.get("email", "")
        )

        return {
            "exito": True,
            "usuario_id": usuario["usuario_id"],
            "nombre": usuario["nombre"],
            "nombre_original": usuario.get("nombre_original", usuario["nombre"]),
            "email": usuario.get("email", ""),
            "token": token,
            "mensaje": "Sesión iniciada correctamente",
        }

    # ==========================================
    #  VERIFICACIÓN
    # ==========================================

    def verificar_sesion(self, token: str) -> Optional[Dict]:
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
            "email": usuario.get("email", ""),
        }

    # ==========================================
    #  CAMBIAR PASSWORD
    # ==========================================

    def cambiar_password(
        self, nombre: str, password_actual: str, password_nueva: str
    ) -> Dict:
        nombre_normalizado = nombre.lower().strip()

        if nombre_normalizado not in self.usuarios["usuarios"]:
            return {"exito": False, "error": "Usuario no encontrado"}

        usuario = self.usuarios["usuarios"][nombre_normalizado]

        if not verificar_password(password_actual, usuario["password_hash"]):
            return {"exito": False, "error": "Contraseña actual incorrecta"}

        if len(password_nueva) < 6:
            return {
                "exito": False,
                "error": "La nueva contraseña debe tener al menos 6 caracteres",
            }

        usuario["password_hash"] = hash_password(password_nueva)
        self._guardar_usuarios()

        return {"exito": True, "mensaje": "Contraseña actualizada"}

    # ==========================================
    #  UTILIDADES
    # ==========================================

    def listar_usuarios_publicos(self) -> list:
        """Lista usuarios SIN información sensible"""
        return [
            {
                "nombre": u["nombre"],
                "nombre_original": u.get("nombre_original", u["nombre"]),
            }
            for u in self.usuarios["usuarios"].values()
            if u.get("activo", True)
        ]

    def obtener_usuario(self, nombre: str) -> Optional[Dict]:
        """Obtiene un usuario por nombre (sin password_hash)"""
        nombre_normalizado = nombre.lower().strip()

        if nombre_normalizado not in self.usuarios["usuarios"]:
            return None

        usuario = self.usuarios["usuarios"][nombre_normalizado].copy()
        usuario.pop("password_hash", None)  # No exponer el hash
        return usuario


# ============================================
#  DEPENDENCIA PARA FASTAPI
# ============================================


async def obtener_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict:
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
        "email": payload.get("email", ""),
    }
