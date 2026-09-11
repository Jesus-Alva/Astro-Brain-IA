# ============================================
#  SISTEMA DE FEEDBACK INTELIGENTE
#  El feedback se usa para mejorar las respuestas
# ============================================

from datetime import datetime
from typing import Dict, List, Optional
import json
import os
from utils import Utils


class Feedback:
    def __init__(self, memoria_vectorial, directorio="conocimiento/"):
        self.memoria = memoria_vectorial
        self.directorio = directorio
        self.archivo_feedback = f"{directorio}feedback.json"
        self.datos = self._cargar_feedback()
        self._sincronizar_estadisticas()
        self._sincronizar_patrones()

    def _cargar_feedback(self) -> Dict:
        """Carga el archivo de feedback"""
        if os.path.exists(self.archivo_feedback):
            try:
                return Utils.cargar_json(self.archivo_feedback)
            except:
                return self._estructura_base()
        return self._estructura_base()

    def _estructura_base(self) -> Dict:
        return {
            "metadata": {
                "creado": datetime.now().isoformat(),
                "ultima_actualizacion": datetime.now().isoformat(),
            },
            "feedback": [],  # Lista de feedbacks
            "patrones": {
                "positivos": [],  # Patrones que funcionan
                "negativos": [],  # Patrones a evitar
            },
            "estadisticas": {"total": 0, "positivos": 0, "negativos": 0},
        }

    def _sincronizar_estadisticas(self):
        feedbacks = self.datos.get("feedback", [])
        self.datos["estadisticas"] = {
            "total": len(feedbacks),
            "positivos": sum(1 for item in feedbacks if item.get("es_positivo")),
            "negativos": sum(1 for item in feedbacks if not item.get("es_positivo")),
        }

    def _sincronizar_patrones(self):
        feedbacks = self.datos.get("feedback", [])
        self.datos["patrones"] = {
            "positivos": [
                self._extraer_patron(item.get("mensaje", ""), item.get("respuesta", ""))
                for item in feedbacks
                if item.get("es_positivo")
            ][-100:],
            "negativos": [
                self._extraer_patron(item.get("mensaje", ""), item.get("respuesta", ""))
                for item in feedbacks
                if not item.get("es_positivo")
            ][-100:],
        }

    def _guardar(self):
        """Guarda el feedback en disco"""
        self.datos["metadata"]["ultima_actualizacion"] = datetime.now().isoformat()
        Utils.guardar_json(self.datos, self.archivo_feedback)

    def registrar_feedback(
        self,
        mensaje: str,
        respuesta: str,
        es_positivo: bool,
        usuario: str = "anonimo",
        contexto: Optional[Dict] = None,
    ) -> Dict:
        """Registra feedback y extrae patrones"""
        feedback = {
            "id": f"fb_{datetime.now().timestamp()}",
            "mensaje": mensaje,
            "respuesta": respuesta,
            "es_positivo": es_positivo,
            "usuario": usuario,
            "timestamp": datetime.now().isoformat(),
            "contexto": contexto or {},
        }

        # Guardar en la lista
        self.datos["feedback"].append(feedback)

        # Actualizar estadísticas
        self.datos["estadisticas"]["total"] += 1
        if es_positivo:
            self.datos["estadisticas"]["positivos"] += 1
        else:
            self.datos["estadisticas"]["negativos"] += 1

        # Extraer patrón
        patron = self._extraer_patron(mensaje, respuesta)
        if es_positivo:
            self.datos["patrones"]["positivos"].append(patron)
        else:
            self.datos["patrones"]["negativos"].append(patron)

        # Mantener solo los últimos 100 patrones
        self.datos["patrones"]["positivos"] = self.datos["patrones"]["positivos"][-100:]
        self.datos["patrones"]["negativos"] = self.datos["patrones"]["negativos"][-100:]

        # Guardar en memoria vectorial también
        try:
            self.memoria.guardar_conocimiento(
                texto=f"[{'POSITIVO' if es_positivo else 'NEGATIVO'}] Pregunta: {mensaje[:100]} | Respuesta: {respuesta[:100]}",
                categoria="feedback",
                etiquetas=["feedback", "positivo" if es_positivo else "negativo"],
                importancia=8 if es_positivo else 6,
                confianza=0.9,
                usuario_id=usuario,  # ✅ NUEVO: AISLAMIENTO POR USUARIO
                metadata_extra={
                    "tipo": "feedback",
                    "es_positivo": es_positivo,
                    "usuario": usuario,
                },
            )
        except Exception as e:
            print(f"⚠️ Error guardando feedback en memoria: {e}")

        self._guardar()

        return {
            "feedback_registrado": True,
            "es_positivo": es_positivo,
            "total_feedbacks": self.datos["estadisticas"]["total"],
            "fecha": feedback["timestamp"],
        }

    def _extraer_patron(self, mensaje: str, respuesta: str) -> Dict:
        """Extrae un patrón de la conversación"""
        return {
            "mensaje_preview": mensaje[:100],
            "respuesta_preview": respuesta[:100],
            "longitud_mensaje": len(mensaje),
            "longitud_respuesta": len(respuesta),
            "timestamp": datetime.now().isoformat(),
        }

    def obtener_estadisticas(self, usuario: Optional[str] = None) -> Dict:
        """Obtiene estadísticas del feedback, opcionalmente filtradas por usuario"""
        if usuario:
            feedbacks = [
                f for f in self.datos["feedback"] if f.get("usuario") == usuario
            ]
            total = len(feedbacks)
            positivos = len([f for f in feedbacks if f.get("es_positivo")])
            negativos = total - positivos
        else:
            stats = self.datos["estadisticas"]
            total = stats["total"]
            positivos = stats["positivos"]
            negativos = stats["negativos"]

        return {
            "total_feedback": total,
            "positivos": positivos,
            "negativos": negativos,
            "tasa_aceptacion": round((positivos / total * 100) if total > 0 else 0, 2),
            "patrones_positivos": len(self.datos["patrones"]["positivos"]),
            "patrones_negativos": len(self.datos["patrones"]["negativos"]),
            "usuario": usuario or "todos",  # ✅ NUEVO
        }

    def obtener_consejos(
        self, consulta: str, n: int = 3, usuario: Optional[str] = None
    ) -> str:
        """
        Obtiene consejos basados en feedback anterior.
        Se usa para mejorar el prompt de la IA.
        """
        # Buscar feedback similar
        try:
            usuario_busqueda = usuario or getattr(
                self.memoria, "usuario_actual", "anonimo"
            )
            feedbacks_relevantes = self.memoria.buscar_semantico(
                f"feedback {consulta}", n_resultados=n * 2, usuario_id=usuario_busqueda
            )

            positivos = []
            negativos = []

            for fb in feedbacks_relevantes:
                es_positivo = fb["metadata"].get("es_positivo", False)
                doc = fb["documento"]

                if es_positivo:
                    positivos.append(doc)
                else:
                    negativos.append(doc)

            consejos = ""
            if positivos:
                consejos += (
                    "\n✅ RESPUESTAS QUE FUERON BIEN RECIBIDAS (úsalas como ejemplo):\n"
                )
                for i, p in enumerate(positivos[:n], 1):
                    consejos += f"{i}. {p}\n"

            if negativos:
                consejos += "\n❌ RESPUESTAS QUE NO GUSTARON (evítalas):\n"
                for i, n_item in enumerate(negativos[:n], 1):
                    consejos += f"{i}. {n_item}\n"

            return consejos
        except Exception as e:
            print(f"⚠️ Error obteniendo consejos: {e}")
            return ""

    def obtener_historial(self, usuario: str = None, limite: int = 20) -> List[Dict]:
        """Obtiene el historial de feedback"""
        feedbacks = self.datos["feedback"]

        if usuario:
            feedbacks = [f for f in feedbacks if f.get("usuario") == usuario]

        return feedbacks[-limite:][::-1]  # Más recientes primero

    def limpiar_feedback(self, usuario: str = None) -> Dict:
        """Limpia el feedback (opcional por usuario)"""
        if usuario:
            antes = len(self.datos["feedback"])
            self.datos["feedback"] = [
                f for f in self.datos["feedback"] if f.get("usuario") != usuario
            ]
            eliminados = antes - len(self.datos["feedback"])
            self._sincronizar_estadisticas()
            self._sincronizar_patrones()
        else:
            eliminados = len(self.datos["feedback"])
            self.datos = self._estructura_base()

        self._guardar()
        return {"eliminados": eliminados, "mensaje": "Feedback limpiado"}
