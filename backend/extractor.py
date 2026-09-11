# ============================================
#  EXTRACTOR INTELIGENTE DE CONOCIMIENTO
#  Usa la IA para extraer, clasificar y etiquetar información
# ============================================

import ollama
import json
from typing import List, Dict, Optional
from utils import Utils


class ExtractorInteligente:
    def __init__(self, modelo: str = "mistral"):
        self.modelo = modelo
        self.config = Utils.cargar_config()

        # Definición de categorías con descripciones
        self.categorias = {
            "datos_personales": "Nombre, edad, ubicación, profesión, familia, etc.",
            "gustos_y_preferencias": "Comida, música, películas, hobbies, deportes, etc.",
            "conocimiento_tecnico": "Lenguajes, frameworks, herramientas, proyectos técnicos",
            "metas_y_proyectos": "Objetivos, planes, sueños, proyectos en curso",
            "opiniones": "Creencias, valores, puntos de vista, críticas",
            "relaciones": "Amigos, familia, colegas, mascotas",
            "salud": "Ejercicio, dieta, condiciones médicas, hábitos",
            "general": "Información que no encaja en otras categorías",
        }

    def extraer_conocimiento(self, conversacion: List[Dict]) -> Dict:
        """
        Extrae conocimiento estructurado de una conversación usando la IA.

        Retorna:
        {
            "items": [
                {
                    "texto": "Al usuario le gusta el rock",
                    "categoria": "gustos_y_preferencias",
                    "etiquetas": ["música", "rock", "preferencias"],
                    "importancia": 8,
                    "confianza": 0.9
                }
            ],
            "resumen": "El usuario compartió sus gustos musicales y datos personales"
        }
        """
        # Preparar el texto de la conversación
        texto_conversacion = self._formatear_conversacion(conversacion)

        # Prompt para la IA
        prompt = self._construir_prompt_extraccion(texto_conversacion)

        try:
            # Llamar a la IA
            respuesta = ollama.chat(
                model=self.modelo,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un extractor de conocimiento experto. Tu trabajo es analizar conversaciones y extraer información estructurada en formato JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                options={"temperature": 0.2},  # Baja temperatura para más precisión
            )

            texto_respuesta = respuesta["message"]["content"]

            # Parsear JSON
            datos = self._parsear_json(texto_respuesta)

            if datos:
                # Validar y normalizar
                datos = self._validar_extraccion(datos)
                return datos
            else:
                # Fallback: extracción básica
                return self._extraccion_fallback(conversacion)

        except Exception as e:
            print(f"⚠️ Error en extracción: {e}")
            return self._extraccion_fallback(conversacion)

    def _formatear_conversacion(self, conversacion: List[Dict]) -> str:
        """Formatea la conversación para el prompt"""
        lineas = []
        for msg in conversacion:
            rol = "Usuario" if msg["role"] == "user" else "IA"
            lineas.append(f"{rol}: {msg['content']}")
        return "\n".join(lineas)

    def _construir_prompt_extraccion(self, conversacion: str) -> str:
        """Construye el prompt para extraer conocimiento"""
        categorias_str = "\n".join(
            [f"- {cat}: {desc}" for cat, desc in self.categorias.items()]
        )

        return f"""Analiza esta conversación y extrae TODA la información relevante sobre el usuario.

            CATEGORÍAS DISPONIBLES:
            {categorias_str}

            CONVERSACIÓN:
            {conversacion}

            INSTRUCCIONES:
            1. Extrae cada pieza de información como un item separado
            2. Asigna una categoría a cada item
            3. Genera 3-5 etiquetas (tags) descriptivas en minúsculas sin espacios
            4. Asigna un score de importancia del 1 al 10:
            - 10: Información muy personal o crítica
            - 7-9: Datos importantes (nombre, gustos fuertes, metas)
            - 4-6: Datos útiles pero no críticos
            - 1-3: Información trivial
            5. Asigna un score de confianza del 0.0 al 1.0 (qué tan seguro estás)

            RESPONDE ÚNICAMENTE CON ESTE FORMATO JSON (sin texto adicional):
            {{
            "items": [
                {{
                "texto": "Descripción clara de la información",
                "categoria": "una_de_las_categorias",
                "etiquetas": ["tag1", "tag2", "tag3"],
                "importancia": 8,
                "confianza": 0.9
                }}
            ],
            "resumen": "Resumen de 1 frase sobre lo aprendido"
            }}

            Ejemplo de salida:
            {{
            "items": [
                {{
                "texto": "El usuario se llama Carlos",
                "categoria": "datos_personales",
                "etiquetas": ["nombre", "identidad", "carlos"],
                "importancia": 10,
                "confianza": 1.0
                }},
                {{
                "texto": "Al usuario le gusta la música rock, especialmente Queen",
                "categoria": "gustos_y_preferencias",
                "etiquetas": ["musica", "rock", "queen"],
                "importancia": 8,
                "confianza": 0.95
                }}
            ],
            "resumen": "El usuario compartió su nombre y gustos musicales"
            }}
            """

    def _parsear_json(self, texto: str) -> Optional[Dict]:
        """Parsea el JSON de la respuesta de la IA"""
        try:
            # Buscar el JSON en la respuesta
            inicio = texto.find("{")
            fin = texto.rfind("}") + 1

            if inicio == -1 or fin == 0:
                return None

            json_str = texto[inicio:fin]
            return json.loads(json_str)

        except json.JSONDecodeError as e:
            print(f"⚠️ Error parseando JSON: {e}")
            return None

    def _validar_extraccion(self, datos: Dict) -> Dict:
        """Valida y normaliza los datos extraídos"""
        if "items" not in datos:
            datos["items"] = []

        if "resumen" not in datos:
            datos["resumen"] = "Sin resumen"

        # Validar cada item
        items_validados = []
        for item in datos["items"]:
            # Validar campos requeridos
            if "texto" not in item or not item["texto"]:
                continue

            # Normalizar categoría
            categoria = item.get("categoria", "general").lower()
            if categoria not in self.categorias:
                categoria = "general"

            # Normalizar etiquetas
            etiquetas = item.get("etiquetas", [])
            if not isinstance(etiquetas, list):
                etiquetas = []
            etiquetas = [
                tag.lower().strip().replace(" ", "_") for tag in etiquetas if tag
            ][
                :5
            ]  # Máximo 5 etiquetas

            # Normalizar importancia
            try:
                importancia = int(item.get("importancia", 5))
                importancia = max(1, min(10, importancia))
            except:
                importancia = 5

            # Normalizar confianza
            try:
                confianza = float(item.get("confianza", 0.7))
                confianza = max(0.0, min(1.0, confianza))
            except:
                confianza = 0.7

            items_validados.append(
                {
                    "texto": item["texto"],
                    "categoria": categoria,
                    "etiquetas": etiquetas,
                    "importancia": importancia,
                    "confianza": confianza,
                }
            )

        return {
            "items": items_validados,
            "resumen": datos.get("resumen", "Sin resumen"),
        }

    def _extraccion_fallback(self, conversacion: List[Dict]) -> Dict:
        """Extracción básica si la IA falla"""
        items = []

        # Extraer información básica de los mensajes del usuario
        for msg in conversacion:
            if msg["role"] != "user":
                continue

            contenido = msg["content"]

            # Detectar patrones básicos
            if any(p in contenido.lower() for p in ["me llamo", "mi nombre es"]):
                items.append(
                    {
                        "texto": contenido,
                        "categoria": "datos_personales",
                        "etiquetas": ["nombre", "identidad"],
                        "importancia": 10,
                        "confianza": 0.8,
                    }
                )
            elif any(p in contenido.lower() for p in ["me gusta", "prefiero", "odio"]):
                items.append(
                    {
                        "texto": contenido,
                        "categoria": "gustos_y_preferencias",
                        "etiquetas": ["preferencias"],
                        "importancia": 7,
                        "confianza": 0.7,
                    }
                )
            elif any(p in contenido.lower() for p in ["trabajo", "proyecto", "meta"]):
                items.append(
                    {
                        "texto": contenido,
                        "categoria": "metas_y_proyectos",
                        "etiquetas": ["proyectos"],
                        "importancia": 8,
                        "confianza": 0.7,
                    }
                )

        return {"items": items, "resumen": "Extracción básica (IA no disponible)"}

    def priorizar_conocimiento(self, items: List[Dict]) -> List[Dict]:
        """
        Prioriza los items por importancia y confianza.
        Filtra items con baja importancia.
        """
        # Filtrar items con importancia menor a 4 y confianza menor a 0.5
        items_filtrados = [
            item
            for item in items
            if item.get("importancia", 5) >= 4 and item.get("confianza", 0.7) >= 0.5
        ]

        # Ordenar por importancia y confianza
        items_ordenados = sorted(
            items_filtrados,
            key=lambda x: (x.get("importancia", 5), x.get("confianza", 0.7)),
            reverse=True,
        )

        return items_ordenados
