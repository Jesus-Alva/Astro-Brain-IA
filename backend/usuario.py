import json
import os
import uuid
from datetime import datetime
from typing import Dict, Optional, List
from utils import Utils


class Usuario:
    def __init__(self, directorio="conocimiento/"):
        self.directorio = directorio
        self.usuario_actual = None
        self._crear_directorio()

    def _crear_directorio(self):
        if not os.path.exists(self.directorio):
            os.makedirs(self.directorio)

    def crear_usuario(self, nombre: str) -> Dict:
        usuario_id = str(uuid.uuid4())[:8]
        perfil = {
            "id": usuario_id,
            "nombre": nombre,
            "creado": datetime.now().isoformat(),
            "ultima_interaccion": datetime.now().isoformat(),
            "preferencias": {"personalidad": "amigable", "temperatura": 0.7},
            "estadisticas": {
                "total_conversaciones": 0,
                "total_mensajes": 0,
                "feedback_positivo": 0,
                "feedback_negativo": 0,
            },
        }

        archivo = f"{self.directorio}{nombre}_{usuario_id}.json"
        Utils.guardar_json(perfil, archivo)
        return perfil

    def cargar_usuario(self, nombre: str) -> Optional[Dict]:
        if not os.path.exists(self.directorio):
            return None

        archivos = [
            f
            for f in os.listdir(self.directorio)
            if f.endswith(".json") and f.startswith(nombre)
        ]
        if not archivos:
            return None

        archivo = archivos[0]
        perfil = Utils.cargar_json(f"{self.directorio}{archivo}")
        if perfil:
            self.usuario_actual = perfil
        return perfil

    def listar_usuarios(self) -> List[Dict]:
        usuarios = []
        if not os.path.exists(self.directorio):
            return usuarios

        for archivo in os.listdir(self.directorio):
            if archivo.endswith(".json"):
                try:
                    perfil = Utils.cargar_json(f"{self.directorio}{archivo}")
                    if perfil:
                        usuarios.append(
                            {
                                "nombre": perfil.get("nombre", "desconocido"),
                                "id": perfil.get("id", "sin_id"),
                                "creado": perfil.get("creado", "desconocido"),
                            }
                        )
                except:
                    continue
        return usuarios
