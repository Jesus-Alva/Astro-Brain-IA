# ============================================
#  GESTOR DE CONVERSACIONES
#  Cada usuario puede tener múltiples conversaciones
# ============================================

import os
import uuid
import json
from datetime import datetime
from typing import List, Dict, Optional
from utils import Utils


class GestorConversaciones:
    """
    Gestiona las conversaciones de cada usuario.

    Estructura de archivos:
    conocimiento/
    ├── conversaciones/
    │   ├── jesus_conversaciones.json
    │   ├── maria_conversaciones.json
    │   └── ...
    """

    def __init__(self, directorio: str = "conocimiento/"):
        self.directorio = directorio
        self.directorio_conv = f"{directorio}conversaciones/"
        self._crear_directorio()

    def _crear_directorio(self):
        """Crea el directorio de conversaciones"""
        os.makedirs(self.directorio_conv, exist_ok=True)

    def _archivo_usuario(self, usuario: str) -> str:
        """Devuelve la ruta del archivo de conversaciones de un usuario"""
        nombre_seguro = "".join(c for c in usuario if c.isalnum() or c in "._-")
        return f"{self.directorio_conv}{nombre_seguro}_conversaciones.json"

    def _cargar(self, usuario: str) -> Dict:
        """Carga las conversaciones de un usuario"""
        archivo = self._archivo_usuario(usuario)

        if not os.path.exists(archivo):
            return {
                "usuario": usuario,
                "creado": datetime.now().isoformat(),
                "ultima_actualizacion": datetime.now().isoformat(),
                "conversaciones": [],
            }

        try:
            return Utils.cargar_json(archivo)
        except Exception as e:
            print(f"⚠️ Error cargando conversaciones de {usuario}: {e}")
            return {
                "usuario": usuario,
                "creado": datetime.now().isoformat(),
                "ultima_actualizacion": datetime.now().isoformat(),
                "conversaciones": [],
            }

    def _guardar(self, usuario: str, datos: Dict):
        """Guarda las conversaciones de un usuario"""
        archivo = self._archivo_usuario(usuario)
        datos["ultima_actualizacion"] = datetime.now().isoformat()
        Utils.guardar_json(datos, archivo)

    # ==========================================
    #  CRUD DE CONVERSACIONES
    # ==========================================

    def crear_conversacion(
        self, usuario: str, titulo: Optional[str] = None, personalidad: str = "amigable"
    ) -> Dict:
        """
        Crea una nueva conversación para un usuario.

        Returns:
            {
                "id": "conv_abc12345",
                "titulo": "Nueva conversación",
                "creada": "...",
                "actualizada": "...",
                "personalidad": "amigable",
                "mensajes": [],
                "metadata": {...}
            }
        """
        datos = self._cargar(usuario)

        # Generar ID único
        conv_id = f"conv_{str(uuid.uuid4())[:8]}"

        # Título por defecto
        if not titulo:
            # Contar conversaciones existentes
            num = len(datos["conversaciones"]) + 1
            titulo = f"Conversación {num}"

        conversacion = {
            "id": conv_id,
            "titulo": titulo,
            "creada": datetime.now().isoformat(),
            "actualizada": datetime.now().isoformat(),
            "personalidad": personalidad,
            "mensajes": [],
            "metadata": {
                "total_mensajes": 0,
                "total_hechos": 0,
                "archivada": False,
                "destacada": False,
            },
        }

        # Añadir al inicio de la lista (más reciente primero)
        datos["conversaciones"].insert(0, conversacion)
        self._guardar(usuario, datos)

        return conversacion

    def listar_conversaciones(
        self, usuario: str, incluir_archivadas: bool = False, limite: int = 100
    ) -> List[Dict]:
        """
        Lista todas las conversaciones de un usuario.
        Devuelve la metadata sin los mensajes completos.
        """
        datos = self._cargar(usuario)

        conversaciones = datos["conversaciones"]

        # Filtrar archivadas
        if not incluir_archivadas:
            conversaciones = [
                c
                for c in conversaciones
                if not c.get("metadata", {}).get("archivada", False)
            ]

        # Limitar
        conversaciones = conversaciones[:limite]

        # Devolver solo metadata (sin mensajes)
        resultado = []
        for conv in conversaciones:
            resultado.append(
                {
                    "id": conv["id"],
                    "titulo": conv["titulo"],
                    "creada": conv["creada"],
                    "actualizada": conv["actualizada"],
                    "personalidad": conv.get("personalidad", "amigable"),
                    "total_mensajes": len(conv.get("mensajes", [])),
                    "metadata": conv.get("metadata", {}),
                    "ultimo_mensaje": self._obtener_ultimo_mensaje(conv),
                }
            )

        return resultado

    def _obtener_ultimo_mensaje(self, conversacion: Dict) -> Optional[str]:
        """Obtiene el último mensaje de una conversación (vista previa)"""
        mensajes = conversacion.get("mensajes", [])
        if not mensajes:
            return None

        ultimo = mensajes[-1]
        contenido = ultimo.get("content", "")[:80]
        return contenido

    def obtener_conversacion(self, usuario: str, conv_id: str) -> Optional[Dict]:
        """Obtiene una conversación completa (con todos los mensajes)"""
        datos = self._cargar(usuario)

        for conv in datos["conversaciones"]:
            if conv["id"] == conv_id:
                return conv

        return None

    def agregar_mensaje(
        self,
        usuario: str,
        conv_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None,
    ) -> Optional[Dict]:
        """
        Agrega un mensaje a una conversación.

        Returns:
            El mensaje agregado, o None si no se encontró la conversación.
        """
        datos = self._cargar(usuario)

        for conv in datos["conversaciones"]:
            if conv["id"] == conv_id:
                mensaje = {
                    "id": f"msg_{str(uuid.uuid4())[:8]}",
                    "role": role,
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": metadata or {},
                }

                conv["mensajes"].append(mensaje)
                conv["actualizada"] = datetime.now().isoformat()
                conv["metadata"]["total_mensajes"] = len(conv["mensajes"])

                # Actualizar título si es el primer mensaje del usuario
                if role == "user" and len(conv["mensajes"]) == 1:
                    titulo_auto = self._generar_titulo(content)
                    if titulo_auto:
                        conv["titulo"] = titulo_auto

                self._guardar(usuario, datos)
                return mensaje

        return None

    def _generar_titulo(self, primer_mensaje: str) -> str:
        """Genera un título automático basado en el primer mensaje"""
        # Limpiar y truncar
        titulo = primer_mensaje.strip()

        # Quitar saltos de línea
        titulo = " ".join(titulo.split())

        # Truncar a 50 caracteres
        if len(titulo) > 50:
            titulo = titulo[:47] + "..."

        return titulo if titulo else "Nueva conversación"

    def actualizar_conversacion(
        self, usuario: str, conv_id: str, cambios: Dict
    ) -> Optional[Dict]:
        """
        Actualiza los metadatos de una conversación.

        Cambios permitidos:
        - titulo: str
        - personalidad: str
        - archivada: bool
        - destacada: bool
        """
        datos = self._cargar(usuario)

        for conv in datos["conversaciones"]:
            if conv["id"] == conv_id:
                # Actualizar título
                if "titulo" in cambios:
                    conv["titulo"] = cambios["titulo"]

                # Actualizar personalidad
                if "personalidad" in cambios:
                    conv["personalidad"] = cambios["personalidad"]

                # Actualizar metadata
                if "archivada" in cambios:
                    conv["metadata"]["archivada"] = cambios["archivada"]

                if "destacada" in cambios:
                    conv["metadata"]["destacada"] = cambios["destacada"]

                conv["actualizada"] = datetime.now().isoformat()
                self._guardar(usuario, datos)
                return conv

        return None

    def eliminar_conversacion(self, usuario: str, conv_id: str) -> bool:
        """
        Elimina una conversación permanentemente.

        Returns:
            True si se eliminó, False si no se encontró.
        """
        datos = self._cargar(usuario)

        conversaciones_antes = len(datos["conversaciones"])
        datos["conversaciones"] = [
            c for c in datos["conversaciones"] if c["id"] != conv_id
        ]

        if len(datos["conversaciones"]) < conversaciones_antes:
            self._guardar(usuario, datos)
            return True

        return False

    def eliminar_todas_conversaciones(self, usuario: str) -> int:
        """Elimina TODAS las conversaciones de un usuario"""
        datos = self._cargar(usuario)
        eliminadas = len(datos["conversaciones"])
        datos["conversaciones"] = []
        self._guardar(usuario, datos)
        return eliminadas

    def buscar_conversaciones(self, usuario: str, termino: str) -> List[Dict]:
        """Busca conversaciones que contengan un término"""
        datos = self._cargar(usuario)
        termino_lower = termino.lower()

        resultados = []
        for conv in datos["conversaciones"]:
            # Buscar en el título
            if termino_lower in conv["titulo"].lower():
                resultados.append(self._metadata_conv(conv))
                continue

            # Buscar en los mensajes
            for msg in conv.get("mensajes", []):
                if termino_lower in msg.get("content", "").lower():
                    resultados.append(self._metadata_conv(conv))
                    break

        return resultados

    def _metadata_conv(self, conv: Dict) -> Dict:
        """Devuelve solo la metadata de una conversación"""
        return {
            "id": conv["id"],
            "titulo": conv["titulo"],
            "creada": conv["creada"],
            "actualizada": conv["actualizada"],
            "personalidad": conv.get("personalidad", "amigable"),
            "total_mensajes": len(conv.get("mensajes", [])),
            "metadata": conv.get("metadata", {}),
            "ultimo_mensaje": self._obtener_ultimo_mensaje(conv),
        }

    def exportar_conversacion(self, usuario: str, conv_id: str) -> Optional[Dict]:
        """Exporta una conversación completa"""
        return self.obtener_conversacion(usuario, conv_id)

    def importar_conversacion(self, usuario: str, conversacion: Dict) -> Optional[Dict]:
        """Importa una conversación desde un JSON"""
        datos = self._cargar(usuario)

        # Generar nuevo ID para evitar colisiones
        conv_id = f"conv_{str(uuid.uuid4())[:8]}"

        conversacion["id"] = conv_id
        conversacion["importada"] = datetime.now().isoformat()

        # Asegurar campos requeridos
        if "creada" not in conversacion:
            conversacion["creada"] = datetime.now().isoformat()
        if "actualizada" not in conversacion:
            conversacion["actualizada"] = datetime.now().isoformat()
        if "mensajes" not in conversacion:
            conversacion["mensajes"] = []
        if "metadata" not in conversacion:
            conversacion["metadata"] = {}

        datos["conversaciones"].insert(0, conversacion)
        self._guardar(usuario, datos)

        return conversacion

    def obtener_estadisticas(self, usuario: str) -> Dict:
        """Obtiene estadísticas de las conversaciones de un usuario"""
        datos = self._cargar(usuario)
        conversaciones = datos["conversaciones"]

        total_mensajes = sum(len(c.get("mensajes", [])) for c in conversaciones)
        total_usuario = sum(
            len([m for m in c.get("mensajes", []) if m.get("role") == "user"])
            for c in conversaciones
        )
        total_asistente = total_mensajes - total_usuario

        return {
            "usuario": usuario,
            "total_conversaciones": len(conversaciones),
            "total_mensajes": total_mensajes,
            "mensajes_usuario": total_usuario,
            "mensajes_asistente": total_asistente,
            "conversaciones_archivadas": sum(
                1
                for c in conversaciones
                if c.get("metadata", {}).get("archivada", False)
            ),
            "conversaciones_destacadas": sum(
                1
                for c in conversaciones
                if c.get("metadata", {}).get("destacada", False)
            ),
        }
