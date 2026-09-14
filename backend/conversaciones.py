import os
import uuid
from datetime import datetime
from threading import RLock
from typing import Dict, List, Optional

from utils import Utils


class GestorConversaciones:
    """Persiste conversaciones completas separadas por usuario."""

    def __init__(self, directorio: str = "conocimiento/"):
        self.directorio = directorio
        self._lock = RLock()
        os.makedirs(self.directorio, exist_ok=True)

    def _archivo(self, usuario: str) -> str:
        seguro = "".join(caracter for caracter in usuario if caracter.isalnum() or caracter in "-_@").strip()
        return os.path.join(self.directorio, f"conversaciones_{seguro}.json")

    def _cargar(self, usuario: str) -> Dict[str, Dict]:
        datos = Utils.cargar_json(self._archivo(usuario))
        return datos if isinstance(datos, dict) else {}

    def _guardar(self, usuario: str, conversaciones: Dict[str, Dict]):
        Utils.guardar_json(conversaciones, self._archivo(usuario))

    def listar(self, usuario: str) -> List[Dict]:
        with self._lock:
            conversaciones = self._cargar(usuario)
            return [self._resumen(conversacion) for conversacion in sorted(
                conversaciones.values(),
                key=lambda item: item.get("actualizada", ""),
                reverse=True,
            )]

    def crear(self, usuario: str, titulo: str = "Nueva conversación") -> Dict:
        ahora = datetime.now().isoformat()
        conversacion = {
            "id": str(uuid.uuid4()),
            "titulo": titulo.strip() or "Nueva conversación",
            "creada": ahora,
            "actualizada": ahora,
            "mensajes": [],
        }
        with self._lock:
            conversaciones = self._cargar(usuario)
            conversaciones[conversacion["id"]] = conversacion
            self._guardar(usuario, conversaciones)
        return conversacion

    def obtener(self, usuario: str, conversacion_id: str) -> Optional[Dict]:
        with self._lock:
            return self._cargar(usuario).get(conversacion_id)

    def guardar_mensaje(
        self,
        usuario: str,
        conversacion_id: str,
        rol: str,
        contenido: str,
        timestamp: Optional[str] = None,
    ) -> Dict:
        with self._lock:
            conversaciones = self._cargar(usuario)
            conversacion = conversaciones.get(conversacion_id)
            if not conversacion:
                raise KeyError("Conversación no encontrada")

            mensaje = {
                "id": str(uuid.uuid4()),
                "role": rol,
                "content": contenido,
                "timestamp": timestamp or datetime.now().isoformat(),
            }
            conversacion["mensajes"].append(mensaje)
            if rol == "user" and len(conversacion["mensajes"]) == 1:
                conversacion["titulo"] = self._titulo_desde_mensaje(contenido)
            conversacion["actualizada"] = datetime.now().isoformat()
            self._guardar(usuario, conversaciones)
            return mensaje

    def renombrar(self, usuario: str, conversacion_id: str, titulo: str) -> Optional[Dict]:
        titulo_limpio = titulo.strip()
        if not titulo_limpio:
            raise ValueError("El nombre de la conversación no puede estar vacío")

        with self._lock:
            conversaciones = self._cargar(usuario)
            conversacion = conversaciones.get(conversacion_id)
            if not conversacion:
                return None
            conversacion["titulo"] = titulo_limpio[:80]
            conversacion["actualizada"] = datetime.now().isoformat()
            self._guardar(usuario, conversaciones)
            return self._resumen(conversacion)

    @staticmethod
    def _titulo_desde_mensaje(contenido: str) -> str:
        palabras = contenido.strip().split()
        titulo = "".join(palabra[0] for palabra in palabras if palabra)
        return titulo[:40] or "Nueva conversación"

    def eliminar(self, usuario: str, conversacion_id: str) -> bool:
        with self._lock:
            conversaciones = self._cargar(usuario)
            if conversacion_id not in conversaciones:
                return False
            del conversaciones[conversacion_id]
            self._guardar(usuario, conversaciones)
            return True

    @staticmethod
    def _resumen(conversacion: Dict) -> Dict:
        return {
            "id": conversacion["id"],
            "titulo": conversacion.get("titulo", "Nueva conversación"),
            "creada": conversacion.get("creada"),
            "actualizada": conversacion.get("actualizada"),
            "total_mensajes": len(conversacion.get("mensajes", [])),
        }
