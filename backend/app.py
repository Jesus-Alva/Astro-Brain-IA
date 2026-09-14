from fastapi import (
    Depends,
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    Query,
    UploadFile,
    File,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from auth import AuthManager, obtener_usuario_actual
from pydantic import BaseModel
import json
import uvicorn


from ia_core import IACore
from usuario import Usuario
from utils import Utils

# Inicializar
app = FastAPI(title="Astro-IA API", version="3.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancias globales
ia = IACore()
gestor_usuarios = Usuario()


# --- Modelos Pydantic ---
class MensajeRequest(BaseModel):
    mensaje: str
    usuario: Optional[str] = "anonimo"
    personalidad: Optional[str] = "amigable"


class FeedbackRequest(BaseModel):
    mensaje: str
    respuesta: str
    es_positivo: bool
    usuario: Optional[str] = "anonimo"


class UsuarioCreate(BaseModel):
    nombre: str


# --- WebSocket ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, websocket: WebSocket, message: str):
        await websocket.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                mensaje = payload.get("mensaje", "")
                usuario = payload.get("usuario", "anonimo")

                # Cambiar usuario
                if usuario != "anonimo":
                    perfil = gestor_usuarios.cargar_usuario(usuario)
                    if perfil:
                        ia.usuario_actual = perfil

                # Generar respuesta
                respuesta = ia.pensar(mensaje)

                # Enviar respuesta
                await manager.send_message(
                    websocket,
                    json.dumps(
                        {
                            "role": "assistant",
                            "content": respuesta,
                            "timestamp": Utils.formatear_fecha(),
                        }
                    ),
                )

            except json.JSONDecodeError:
                await manager.send_message(
                    websocket, json.dumps({"error": "JSON inválido"})
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# --- Endpoints HTTP ---
@app.get("/")
def root():
    return {
        "nombre": "Astro-IA API",
        "version": "3.0",
        "estado": "online",
        "websocket": "/ws",
        "endpoints": ["/chat", "/feedback", "/usuario", "/buscar", "/estadisticas"],
    }


@app.post("/chat")
def chat(request: MensajeRequest, usuario: dict = Depends(obtener_usuario_actual)):
    try:
        usuario_id = usuario.get("nombre")
        ia.set_usuario(usuario_id)
        ia.personalidad = request.personalidad

        respuesta = ia.pensar(request.mensaje)

        return {
            "mensaje": request.mensaje,
            "respuesta": respuesta,
            "usuario": request.usuario,
            "personalidad": ia.personalidad,
            "timestamp": Utils.formatear_fecha(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
def feedback(request: FeedbackRequest, usuario: dict = Depends(obtener_usuario_actual)):
    try:
        return feedback_manager.registrar_feedback(
            mensaje=request.mensaje,
            respuesta=request.respuesta,
            es_positivo=request.es_positivo,
            usuario=usuario["nombre"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/usuario")
def crear_usuario(usuario: UsuarioCreate):
    try:
        perfil = gestor_usuarios.crear_usuario(usuario.nombre)
        return {"mensaje": f"Usuario {usuario.nombre} creado", "perfil": perfil}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/buscar")
def buscar(consulta: str, n_resultados: int = 5):
    try:
        resultados = ia.memoria.buscar_semantico(consulta, n_resultados)
        return {"resultados": resultados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/estadisticas")
def estadisticas(usuario: dict = Depends(obtener_usuario_actual)):
    try:
        ia.set_usuario(usuario["nombre"])
        stats = ia.memoria.obtener_estadisticas()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


@app.get("/buscar/categoria/{categoria}")
def buscar_por_categoria(categoria: str):
    """Busca conocimiento por categoría específica"""
    try:
        items = ia.buscar_por_categoria(categoria)
        return {"categoria": categoria, "total": len(items), "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/buscar/etiqueta/{etiqueta}")
def buscar_por_etiqueta(etiqueta: str):
    """Busca conocimiento por etiqueta específica"""
    try:
        items = ia.buscar_por_etiqueta(etiqueta)
        return {"etiqueta": etiqueta, "total": len(items), "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/etiquetas")
def listar_etiquetas():
    """Lista todas las etiquetas disponibles con su frecuencia"""
    try:
        stats = ia.memoria.obtener_estadisticas()
        return {
            "etiquetas": stats.get("etiquetas", {}),
            "total_unicas": stats.get("total_etiquetas_unicas", 0),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/categorias")
def listar_categorias():
    """Lista todas las categorías con su conteo"""
    try:
        stats = ia.memoria.obtener_estadisticas()
        return {
            "categorias": stats.get("categorias", {}),
            "total_items": stats.get("total_items", 0),
            "importancia_promedio": stats.get("importancia_promedio", 0),
            "confianza_promedio": stats.get("confianza_promedio", 0),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/aprender")
def aprender_manual():
    """Fuerza el aprendizaje manual de la conversación actual"""
    try:
        resultado = ia.aprender_manual()
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
#  ENDPOINTS DE FASE 3: MEMORIA DUAL
# ============================================


@app.get("/memoria/estadisticas")
def estadisticas_memoria_dual(usuario: dict = Depends(obtener_usuario_actual)):
    """Estadísticas de ambas memorias (corto y largo plazo)"""
    try:
        ia.set_usuario(usuario["nombre"])
        return ia.memoria.obtener_estadisticas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memoria/consolidar")
def consolidar_memoria(
    forzar: bool = False, usuario: dict = Depends(obtener_usuario_actual)
):
    """Consolida memoria de corto a largo plazo"""
    try:
        ia.set_usuario(usuario["nombre"])
        return ia.consolidar_memoria(forzar=forzar)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memoria/olvidar")
def olvidar_memoria(
    criterio: str,
    valor: str,
    dry_run: bool = True,
    usuario: dict = Depends(obtener_usuario_actual),
):
    """
    Olvido selectivo de información.

    Criterios:
    - importancia_menor_a: elimina items con importancia < valor
    - confianza_menor_a: elimina items con confianza < valor
    - categoria: elimina items de una categoría
    - etiqueta: elimina items con una etiqueta
    - antiguo_mas_de_dias: elimina items con más de N días
    """
    try:
        # Convertir valor si es necesario
        if criterio in ["importancia_menor_a", "antiguo_mas_de_dias"]:
            valor_conv = int(valor)
        elif criterio == "confianza_menor_a":
            valor_conv = float(valor)
        else:
            valor_conv = valor

        ia.set_usuario(usuario["nombre"])
        return ia.olvidar(criterio, valor_conv, dry_run=dry_run)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memoria/resumen-sesion")
def resumen_sesion(usuario: dict = Depends(obtener_usuario_actual)):
    """Resumen de la sesión actual"""
    try:
        ia.set_usuario(usuario["nombre"])
        return ia.resumen_sesion()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memoria/corto-plazo")
def ver_memoria_corto_plazo(usuario: dict = Depends(obtener_usuario_actual)):
    """Ver items en memoria de corto plazo"""
    try:
        ia.set_usuario(usuario["nombre"])
        return {
            "sesion_id": ia.memoria.corto_plazo.sesion_id,
            "items": ia.memoria.corto_plazo.items,
            "total": ia.memoria.corto_plazo.contar(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memoria/contexto")
def ver_contexto_actual(
    consulta: str = "general", usuario: dict = Depends(obtener_usuario_actual)
):
    """Ver el contexto que la IA usaría para una consulta"""
    try:
        ia.set_usuario(usuario["nombre"])
        return ia.memoria.obtener_contexto_completo(consulta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @app.get("/usuarios")
# def listar_usuarios():
#     """Lista todos los usuarios disponibles"""
#     try:
#         usuarios = gestor_usuarios.listar_usuarios()
#         return {"usuarios": usuarios, "total": len(usuarios)}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# ============================================
#  ENDPOINTS DE FASE 5: PERSONALIZACIÓN
# ============================================

from feedback import Feedback
from fastapi.responses import FileResponse, JSONResponse
import os

# Instancia de feedback
feedback_manager = Feedback(ia.memoria_vectorial)

# --- Feedback ---


@app.get("/feedback/estadisticas")
def estadisticas_feedback():
    """Estadísticas del feedback"""
    try:
        return feedback_manager.obtener_estadisticas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/feedback/historial")
def historial_feedback(usuario: Optional[str] = None, limite: int = 20):
    """Historial de feedback"""
    try:
        return {
            "historial": feedback_manager.obtener_historial(usuario, limite),
            "usuario": usuario or "todos",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback/limpiar")
def limpiar_feedback(usuario: Optional[str] = None):
    """Limpia el feedback"""
    try:
        return feedback_manager.limpiar_feedback(usuario)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Exportación/Importación ---


@app.get("/exportar/conocimiento")
def exportar_conocimiento(usuario: Optional[str] = None):
    """Exporta todo el conocimiento a un archivo JSON"""
    try:
        # Obtener todos los items
        todos = ia.memoria_vectorial.coleccion.get()

        items = []
        if todos["documents"]:
            for i, doc in enumerate(todos["documents"]):
                metadata = todos["metadatas"][i]

                # Filtrar por usuario si se especifica
                if usuario and metadata.get("usuario") != usuario:
                    continue

                items.append(
                    {"id": todos["ids"][i], "texto": doc, "metadata": metadata}
                )

        exportacion = {
            "version": "1.0",
            "fecha": Utils.formatear_fecha(),
            "usuario": usuario or "todos",
            "total_items": len(items),
            "items": items,
        }

        # Guardar archivo temporal
        archivo = f"conocimiento/export_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Utils.guardar_json(exportacion, archivo)

        return FileResponse(
            archivo,
            media_type="application/json",
            filename=f"astro_ia_conocimiento_{datetime.now().strftime('%Y%m%d')}.json",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/importar/conocimiento")
async def importar_conocimiento(archivo: UploadFile = File(...)):
    """Importa conocimiento desde un archivo JSON"""
    try:
        # Leer archivo
        contenido = await archivo.read()
        datos = json.loads(contenido)

        if "items" not in datos:
            raise HTTPException(status_code=400, detail="Formato inválido")

        # Importar items
        importados = 0
        errores = 0

        for item in datos["items"]:
            try:
                metadata = item.get("metadata", {})
                ia.memoria_vectorial.guardar_conocimiento(
                    texto=item["texto"],
                    categoria=metadata.get("categoria", "general"),
                    etiquetas=(
                        metadata.get("etiquetas_str", "").split(",")
                        if metadata.get("etiquetas_str")
                        else []
                    ),
                    importancia=metadata.get("importancia", 5),
                    confianza=metadata.get("confianza", 0.7),
                    metadata_extra={"tipo": "importado", **metadata},
                )
                importados += 1
            except Exception as e:
                errores += 1

        return {
            "importados": importados,
            "errores": errores,
            "total": len(datos["items"]),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Preferencias ---


class PreferenciasRequest(BaseModel):
    usuario: str
    personalidad: Optional[str] = None
    temperatura: Optional[float] = None
    modelo: Optional[str] = None


@app.get("/preferencias/{usuario}")
def obtener_preferencias(usuario: str):
    """Obtiene las preferencias de un usuario"""
    try:
        perfil = gestor_usuarios.cargar_usuario(usuario)
        if perfil:
            return {
                "usuario": usuario,
                "preferencias": perfil.get("preferencias", {}),
                "estadisticas": perfil.get("estadisticas", {}),
            }
        return {"usuario": usuario, "preferencias": {}, "estadisticas": {}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/preferencias")
def actualizar_preferencias(request: PreferenciasRequest):
    """Actualiza las preferencias de un usuario"""
    try:
        perfil = gestor_usuarios.cargar_usuario(request.usuario)
        if not perfil:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if request.personalidad:
            perfil["preferencias"]["personalidad"] = request.personalidad
        if request.temperatura is not None:
            perfil["preferencias"]["temperatura"] = request.temperatura
        if request.modelo:
            perfil["preferencias"]["modelo"] = request.modelo

        gestor_usuarios.actualizar_usuario(perfil)

        return {"actualizado": True, "preferencias": perfil["preferencias"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
#  ENDPOINTS DE FASE 6: MULTIUSUARIO
# ============================================


class CambiarUsuarioRequest(BaseModel):
    usuario: str

@app.get("/usuario/actual")
def usuario_actual():
    """Obtiene el usuario actual"""
    return {
        "usuario_id": ia.usuario_id_actual,
        "personalidad": ia.personalidad,
        "total_mensajes": ia.contador_mensajes,
    }


@app.get("/usuario/aislamiento/verificar")
def verificar_aislamiento(usuario1: str, usuario2: str):
    """
    ✅ VERIFICA EL AISLAMIENTO entre dos usuarios.
    Útil para testing.
    """
    try:
        # Buscar algo del usuario 1
        ia.memoria_vectorial.set_usuario(usuario1)
        items_u1 = ia.memoria_vectorial.buscar_semantico("nombre", n_resultados=5)

        # Buscar algo del usuario 2
        ia.memoria_vectorial.set_usuario(usuario2)
        items_u2 = ia.memoria_vectorial.buscar_semantico("nombre", n_resultados=5)

        # Verificar que no hay solapamiento
        ids_u1 = {item["documento"] for item in items_u1}
        ids_u2 = {item["documento"] for item in items_u2}
        solapamiento = ids_u1 & ids_u2

        return {
            "usuario1": usuario1,
            "usuario2": usuario2,
            "items_usuario1": len(items_u1),
            "items_usuario2": len(items_u2),
            "solapamiento": len(solapamiento),
            "aislamiento_correcto": len(solapamiento) == 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
#  ENDPOINTS DE AUTENTICACIÓN
# ============================================

# Instancia del gestor de autenticación
auth_manager = AuthManager(directorio="conocimiento/")


class RegistroRequest(BaseModel):
    nombre: str
    password: str


class LoginRequest(BaseModel):
    nombre: str
    password: str


class CambiarPasswordRequest(BaseModel):
    password_actual: str
    password_nueva: str


@app.post("/auth/registro")
def registro(request: RegistroRequest):
    """
    Registra un nuevo usuario.

    Ejemplo:
        POST /auth/registro
        {
            "nombre": "jesus",
            "password": "mi_password_segura"
        }
    """
    resultado = auth_manager.registrar(request.nombre, request.password)

    if not resultado["exito"]:
        raise HTTPException(status_code=400, detail=resultado["error"])

    return resultado


@app.post("/auth/login")
def login(request: LoginRequest):
    """
    Inicia sesión con un usuario existente.

    Ejemplo:
        POST /auth/login
        {
            "nombre": "jesus",
            "password": "mi_password_segura"
        }
    """
    resultado = auth_manager.login(request.nombre, request.password)

    if not resultado["exito"]:
        raise HTTPException(status_code=401, detail=resultado["error"])

    return resultado


@app.get("/auth/verificar")
def verificar_sesion(usuario: dict = Depends(obtener_usuario_actual)):
    """
    Verifica que el token sea válido.
    Útil para comprobar si la sesión sigue activa.
    """
    return {"valido": True, "usuario": usuario}


@app.post("/auth/cambiar-password")
def cambiar_password(
    request: CambiarPasswordRequest, usuario: dict = Depends(obtener_usuario_actual)
):
    """Cambia la contraseña del usuario autenticado"""
    resultado = auth_manager.cambiar_password(
        usuario["nombre"], request.password_actual, request.password_nueva
    )

    if not resultado["exito"]:
        raise HTTPException(status_code=400, detail=resultado["error"])

    return resultado


@app.get("/auth/usuarios")
def listar_usuarios():
    """
    Lista usuarios públicos (solo nombres).
    NO expone información sensible.
    """
    return {"usuarios": auth_manager.listar_usuarios_publicos()}
