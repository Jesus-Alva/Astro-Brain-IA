# ============================================
#  MEMORIA DUAL CON SOPORTE MULTIUSUARIO
# ============================================

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import uuid
from utils import Utils


class MemoriaCortoPlazo:
    """Memoria a corto plazo: solo dura la sesión actual."""

    def __init__(self, capacidad_maxima: int = 20):
        self.capacidad = capacidad_maxima
        self.items: List[Dict] = []
        self.sesion_id = str(uuid.uuid4())[:8]
        self.iniciada = datetime.now()

    def agregar(self, contenido: str, tipo: str = "mensaje", metadata: Dict = None):
        item = {
            "id": str(uuid.uuid4())[:8],
            "contenido": contenido,
            "tipo": tipo,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        self.items.append(item)
        if len(self.items) > self.capacidad:
            self.items = self.items[-self.capacidad :]
        return item

    def obtener_reciente(self, n: int = 5) -> List[Dict]:
        return self.items[-n:]

    def obtener_por_tipo(self, tipo: str) -> List[Dict]:
        return [item for item in self.items if item["tipo"] == tipo]

    def limpiar(self):
        self.items = []

    def esta_vacia(self) -> bool:
        return len(self.items) == 0

    def contar(self) -> int:
        return len(self.items)


class MemoriaLargoPlazo:
    """Memoria a largo plazo: persiste entre sesiones."""

    def __init__(self, memoria_vectorial):
        self.memoria_vectorial = memoria_vectorial
        self.consolidaciones_realizadas = 0

    def guardar(
        self,
        contenido: str,
        categoria: str = "general",
        etiquetas: List[str] = None,
        importancia: int = 5,
        confianza: float = 0.7,
        usuario_id: str = None,
        metadata: Dict = None,
    ):
        return self.memoria_vectorial.guardar_conocimiento(
            texto=contenido,
            categoria=categoria,
            etiquetas=etiquetas or [],
            importancia=importancia,
            confianza=confianza,
            usuario_id=usuario_id,
            metadata_extra=metadata or {},
        )

    def buscar(self, consulta: str, n: int = 5, usuario_id: str = None) -> List[Dict]:
        return self.memoria_vectorial.buscar_semantico(
            consulta, n, usuario_id=usuario_id
        )

    def buscar_por_categoria(
        self, categoria: str, usuario_id: str = None
    ) -> List[Dict]:
        return self.memoria_vectorial.buscar_por_categoria(
            categoria, usuario_id=usuario_id
        )

    def buscar_por_etiqueta(self, etiqueta: str, usuario_id: str = None) -> List[Dict]:
        return self.memoria_vectorial.buscar_por_etiqueta(
            etiqueta, usuario_id=usuario_id
        )

    def obtener_estadisticas(self, usuario_id: str = None) -> Dict:
        return self.memoria_vectorial.obtener_estadisticas(usuario_id=usuario_id)


class MemoriaDual:
    """Sistema de memoria dual con soporte multiusuario."""

    def __init__(self, memoria_vectorial):
        self.corto_plazo = MemoriaCortoPlazo(capacidad_maxima=20)
        self.largo_plazo = MemoriaLargoPlazo(memoria_vectorial)
        self.config = Utils.cargar_config()
        self.ultima_consolidacion = datetime.now()
        self.intervalo_consolidacion = timedelta(minutes=5)
        self.usuario_actual = "anonimo"  # ✅ Usuario por defecto

    def set_usuario(self, usuario_id: str):
        """Establece el usuario actual"""
        self.usuario_actual = usuario_id or "anonimo"

    # ==========================================
    #  AGREGAR INFORMACIÓN
    # ==========================================

    def agregar_mensaje(self, contenido: str, rol: str):
        return self.corto_plazo.agregar(
            contenido=contenido, tipo="mensaje", metadata={"role": rol}
        )

    def agregar_hecho(self, hecho: str, categoria: str, etiquetas: List[str] = None):
        return self.corto_plazo.agregar(
            contenido=hecho,
            tipo="hecho",
            metadata={"categoria": categoria, "etiquetas": etiquetas or []},
        )

    # ==========================================
    #  RECUPERAR INFORMACIÓN
    # ==========================================

    def obtener_contexto_completo(
        self, consulta: str, n_corto: int = 5, n_largo: int = 5
    ) -> Dict:
        """Obtiene contexto combinado, filtrado por usuario"""
        contexto_corto = self.corto_plazo.obtener_reciente(n_corto)

        # ✅ Buscar SOLO en el conocimiento del usuario actual
        contexto_largo = self.largo_plazo.buscar(
            consulta, n_largo, usuario_id=self.usuario_actual
        )

        hechos_sesion = self.corto_plazo.obtener_por_tipo("hecho")

        return {
            "conversacion_reciente": contexto_corto,
            "conocimiento_relevante": contexto_largo,
            "hechos_sesion": hechos_sesion,
            "usuario_id": self.usuario_actual,
            "resumen": self._generar_resumen_contexto(contexto_corto, contexto_largo),
        }

    def _generar_resumen_contexto(self, corto: List[Dict], largo: List[Dict]) -> str:
        total_mensajes = len([c for c in corto if c["tipo"] == "mensaje"])
        total_conocimiento = len(largo)
        total_hechos = len([c for c in corto if c["tipo"] == "hecho"])
        return f"{total_mensajes} mensajes recientes, {total_hechos} hechos de sesión, {total_conocimiento} recuerdos relevantes"

    # ==========================================
    #  CONSOLIDACIÓN
    # ==========================================

    def consolidar(self, forzar: bool = False) -> Dict:
        """Consolida hechos de corto plazo a largo plazo CON usuario_id"""
        if not forzar:
            tiempo_desde_ultima = datetime.now() - self.ultima_consolidacion
            if tiempo_desde_ultima < self.intervalo_consolidacion:
                return {"consolidado": False, "razon": "Muy pronto para consolidar"}

        hechos = self.corto_plazo.obtener_por_tipo("hecho")

        if not hechos:
            return {
                "consolidado": False,
                "razon": "No hay hechos para consolidar",
                "items_consolidados": 0,
            }

        consolidados = 0
        errores = 0

        for hecho in hechos:
            try:
                metadata = hecho.get("metadata", {})
                categoria = metadata.get("categoria", "general")
                etiquetas = metadata.get("etiquetas", [])

                # ✅ GUARDAR CON EL USUARIO ACTUAL
                self.largo_plazo.guardar(
                    contenido=hecho["contenido"],
                    categoria=categoria,
                    etiquetas=etiquetas,
                    importancia=7,
                    confianza=0.8,
                    usuario_id=self.usuario_actual,  # ✅ AISLAMIENTO
                    metadata={
                        "tipo": "consolidacion",
                        "sesion_origen": self.corto_plazo.sesion_id,
                        "timestamp_original": hecho["timestamp"],
                    },
                )
                consolidados += 1
            except Exception as e:
                print(f"⚠️ Error consolidando: {e}")
                errores += 1

        # Limpiar hechos consolidados del corto plazo
        self.corto_plazo.items = [
            item for item in self.corto_plazo.items if item["tipo"] != "hecho"
        ]

        self.ultima_consolidacion = datetime.now()
        self.largo_plazo.consolidaciones_realizadas += 1

        return {
            "consolidado": True,
            "items_consolidados": consolidados,
            "errores": errores,
            "usuario_id": self.usuario_actual,
            "timestamp": self.ultima_consolidacion.isoformat(),
        }

    # ==========================================
    #  OLVIDO SELECTIVO
    # ==========================================

    def olvidar(self, criterio: str, valor, dry_run: bool = True) -> Dict:
        """Olvido selectivo, filtrado por usuario actual"""
        if dry_run:
            return self._simular_olvido(criterio, valor)
        return self._ejecutar_olvido(criterio, valor)

    def _simular_olvido(self, criterio: str, valor) -> Dict:
        """Simula el olvido filtrando por usuario"""
        try:
            todos = self.largo_plazo.memoria_vectorial.coleccion.get(
                where={"usuario_id": self.usuario_actual}
            )

            if not todos["metadatas"]:
                return {"eliminaria": 0, "items": [], "usuario_id": self.usuario_actual}

            a_eliminar = []
            for i, meta in enumerate(todos["metadatas"]):
                eliminar = self._cumple_criterio(meta, criterio, valor)
                if eliminar:
                    a_eliminar.append(
                        {
                            "id": todos["ids"][i],
                            "texto": todos["documents"][i][:100],
                            "metadata": meta,
                        }
                    )

            return {
                "criterio": criterio,
                "valor": valor,
                "usuario_id": self.usuario_actual,
                "eliminaria": len(a_eliminar),
                "items": a_eliminar[:10],
            }
        except Exception as e:
            return {"error": str(e), "eliminaria": 0}

    def _ejecutar_olvido(self, criterio: str, valor) -> Dict:
        """Ejecuta el olvido filtrando por usuario"""
        try:
            todos = self.largo_plazo.memoria_vectorial.coleccion.get(
                where={"usuario_id": self.usuario_actual}
            )

            ids_a_eliminar = []
            if todos["metadatas"]:
                for i, meta in enumerate(todos["metadatas"]):
                    if self._cumple_criterio(meta, criterio, valor):
                        ids_a_eliminar.append(todos["ids"][i])

            if ids_a_eliminar:
                self.largo_plazo.memoria_vectorial.coleccion.delete(ids=ids_a_eliminar)

            return {
                "criterio": criterio,
                "valor": valor,
                "usuario_id": self.usuario_actual,
                "eliminados": len(ids_a_eliminar),
            }
        except Exception as e:
            return {"error": str(e), "eliminados": 0}

    def _cumple_criterio(self, meta: Dict, criterio: str, valor) -> bool:
        """Verifica si un item cumple el criterio de olvido"""
        if criterio == "importancia_menor_a":
            return meta.get("importancia", 5) < valor
        elif criterio == "confianza_menor_a":
            return meta.get("confianza", 0.7) < valor
        elif criterio == "categoria":
            return meta.get("categoria") == valor
        elif criterio == "etiqueta":
            etiquetas = meta.get("etiquetas_str", "").split(",")
            return valor in etiquetas
        elif criterio == "antiguo_mas_de_dias":
            try:
                fecha = datetime.fromisoformat(meta.get("timestamp", ""))
                return (datetime.now() - fecha).days > valor
            except:
                return False
        return False

    # ==========================================
    #  RESUMEN DE SESIÓN
    # ==========================================

    def resumen_sesion(self) -> Dict:
        mensajes = [
            item for item in self.corto_plazo.items if item["tipo"] == "mensaje"
        ]
        hechos = [item for item in self.corto_plazo.items if item["tipo"] == "hecho"]

        if not mensajes:
            return {
                "sesion_id": self.corto_plazo.sesion_id,
                "usuario_id": self.usuario_actual,
                "duracion_minutos": 0,
                "total_mensajes": 0,
                "total_hechos": 0,
                "resumen": "Sesión vacía",
            }

        inicio = datetime.fromisoformat(mensajes[0]["timestamp"])
        duracion = (datetime.now() - inicio).seconds // 60

        temas = set()
        for hecho in hechos:
            cat = hecho["metadata"].get("categoria")
            if cat:
                temas.add(cat)

        return {
            "sesion_id": self.corto_plazo.sesion_id,
            "usuario_id": self.usuario_actual,
            "iniciada": self.corto_plazo.iniciada.isoformat(),
            "duracion_minutos": duracion,
            "total_mensajes": len(mensajes),
            "total_hechos": len(hechos),
            "categorias_detectadas": list(temas),
            "primer_mensaje": mensajes[0]["contenido"][:100] if mensajes else "",
            "ultimo_mensaje": mensajes[-1]["contenido"][:100] if mensajes else "",
        }

    # ==========================================
    #  ESTADÍSTICAS
    # ==========================================

    def obtener_estadisticas(self) -> Dict:
        stats_largo = self.largo_plazo.obtener_estadisticas(
            usuario_id=self.usuario_actual
        )

        return {
            "corto_plazo": {
                "sesion_id": self.corto_plazo.sesion_id,
                "usuario_id": self.usuario_actual,
                "items_actuales": self.corto_plazo.contar(),
                "capacidad": self.corto_plazo.capacidad,
                "hechos": len(self.corto_plazo.obtener_por_tipo("hecho")),
                "mensajes": len(self.corto_plazo.obtener_por_tipo("mensaje")),
            },
            "largo_plazo": stats_largo,
            "usuario_id": self.usuario_actual,
            "consolidaciones_realizadas": self.largo_plazo.consolidaciones_realizadas,
            "ultima_consolidacion": self.ultima_consolidacion.isoformat(),
        }
