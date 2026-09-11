import yaml
import json
from datetime import datetime
from typing import Dict, Any


class Utils:
    @staticmethod
    def cargar_config() -> Dict:
        """Carga la configuración desde config.yaml"""
        try:
            with open("config.yaml", "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print("⚠️ config.yaml no encontrado, usando configuración por defecto")
            return {
                "ia": {"nombre": "AstroIA", "modelo": "mistral", "temperatura": 0.7},
                "memoria": {"directorio": "conocimiento/"},
            }

    @staticmethod
    def formatear_fecha() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def guardar_json(datos: Dict, archivo: str):
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)

    @staticmethod
    def cargar_json(archivo: str) -> Dict:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
