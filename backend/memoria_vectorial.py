# ============================================
#  MEMORIA VECTORIAL CON SOPORTE DE ETIQUETAS y MULTIUSUARIO
#  Cada item tiene un usuario_id para aislamiento
# ============================================

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import ollama
import uuid
from datetime import datetime
from utils import Utils


class MemoriaVectorial:
    def __init__(
        self, directorio: str = "conocimiento/", nombre_coleccion: str = "astro_ia"
    ):
        self.directorio = directorio
        self.config = Utils.cargar_config()
        self.usuario_actual = "anonimo"

        self.cliente = chromadb.PersistentClient(
            path=directorio, settings=Settings(anonymized_telemetry=False)
        )

        try:
            self.coleccion = self.cliente.get_collection(nombre_coleccion)
        except:
            self.coleccion = self.cliente.create_collection(
                name=nombre_coleccion, metadata={"hnsw:space": "cosine"}
            )

    def set_usuario(self, usuario_id: str):
        """Establece el usuario actual para el aislamiento de datos"""
        self.usuario_actual = usuario_id or "anonimo"

    def _generar_embedding(self, texto: str) -> List[float]:
        """Genera un embedding para el texto usando Ollama"""
        try:
            respuesta = ollama.embeddings(
                model=self.config["ia"]["modelo"], prompt=texto
            )
            return respuesta["embedding"]
        except Exception as e:
            print(f"⚠️ Error generando embedding: {e}")
            return [0.0] * 384

    def guardar_conocimiento(
        self,
        texto: str,
        categoria: str = "general",
        etiquetas: Optional[List[str]] = None,
        importancia: int = 5,
        confianza: float = 0.7,
        usuario_id: Optional[str] = None,
        metadata_extra: Optional[Dict] = None,
    ) -> str:
        """
        Guarda conocimiento con soporte de etiquetas, importancia y confianza.
        """
        embedding = self._generar_embedding(texto)
        id_unico = str(uuid.uuid4())

        usuario_final = usuario_id or self.usuario_actual

        # Construir metadata
        metadata = {
            "usuario_id": usuario_final,
            "categoria": categoria,
            "timestamp": datetime.now().isoformat(),
            "importancia": importancia,
            "confianza": confianza,
            "etiquetas_str": ",".join(etiquetas or []),  # ChromaDB no acepta listas
            "texto_corto": texto[:200],
        }

        if metadata_extra:
            metadata.update(metadata_extra)

        self.coleccion.add(
            embeddings=[embedding],
            documents=[texto],
            metadatas=[metadata],
            ids=[id_unico],
        )

        return id_unico

    def buscar_semantico(
        self,
        consulta: str,
        n_resultados: int = 5,
        umbral: float = 0.7,
        usuario_id: Optional[str] = None,
    ) -> List[Dict]:
        """Busca conocimiento por similitud semántica"""
        embedding = self._generar_embedding(consulta)

        usuario_final = usuario_id or self.usuario_actual

        try:
            resultados = self.coleccion.query(
                query_embeddings=[embedding],
                n_results=n_resultados,
                where={"usuario_id": usuario_final},
            )
        except Exception as e:
            print(f"⚠️ Error en búsqueda filtrada: {e}")
            # Fallback: buscar sin filtro y filtrar manualmente
            resultados = self.coleccion.query(
                query_embeddings=[embedding], n_results=n_resultados * 3
            )

        items = []
        if resultados["distances"] and resultados["distances"][0]:
            for i, distancia in enumerate(resultados["distances"][0]):
                metadata = resultados["metadatas"][0][i]
                if metadata.get("usuario_id") != usuario_final:
                    continue

                similitud = 1 - distancia
                if similitud >= umbral:
                    items.append(
                        {
                            "documento": resultados["documents"][0][i],
                            "metadata": metadata,
                            "etiquetas": (
                                metadata.get("etiquetas_str", "").split(",")
                                if metadata.get("etiquetas_str")
                                else []
                            ),
                            "importancia": metadata.get("importancia", 5),
                            "similitud": similitud,
                        }
                    )

        # Ordenar por similitud + importancia
        items.sort(key=lambda x: (x["similitud"], x["importancia"]), reverse=True)
        return items

    def buscar_por_categoria(
        self, categoria: str, n_resultados: int = 10, usuario_id: Optional[str] = None
    ) -> List[Dict]:
        """Busca conocimiento por categoría exacta"""
        usuario_final = usuario_id or self.usuario_actual

        try:
            resultados = self.coleccion.get(
                where={
                    "$and": [{"categoria": categoria}, {"usuario_id": usuario_final}]
                },
                limit=n_resultados,
            )

            items = []
            if resultados["documents"]:
                for i, doc in enumerate(resultados["documents"]):
                    metadata = resultados["metadatas"][i]
                    items.append(
                        {
                            "documento": doc,
                            "metadata": metadata,
                            "etiquetas": (
                                metadata.get("etiquetas_str", "").split(",")
                                if metadata.get("etiquetas_str")
                                else []
                            ),
                            "importancia": metadata.get("importancia", 5),
                        }
                    )
            return items
        except Exception as e:
            print(f"⚠️ Error buscando por categoría: {e}")
            return []

    def buscar_por_etiqueta(
        self, etiqueta: str, n_resultados: int = 10, usuario_id: Optional[str] = None
    ) -> List[Dict]:
        """Busca conocimiento por etiqueta específica, filtrado por usuario"""
        usuario_final = usuario_id or self.usuario_actual

        try:
            # ChromaDB no soporta búsqueda LIKE, así que obtenemos todo y filtramos
            resultados = self.coleccion.get(where={"usuario_id": usuario_final})

            items = []
            if resultados["documents"]:
                for i, doc in enumerate(resultados["documents"]):
                    metadata = resultados["metadatas"][i]
                    etiquetas = metadata.get("etiquetas_str", "").split(",")

                    if etiqueta.lower() in [e.lower() for e in etiquetas if e]:
                        items.append(
                            {
                                "documento": doc,
                                "metadata": metadata,
                                "etiquetas": etiquetas,
                                "importancia": metadata.get("importancia", 5),
                            }
                        )

            return items[:n_resultados]
        except Exception as e:
            print(f"⚠️ Error buscando por etiqueta: {e}")
            return []

    def obtener_estadisticas(self, usuario_id: Optional[str] = None) -> Dict:
        """Obtiene estadísticas filtradas por usuario"""
        usuario_final = usuario_id or self.usuario_actual

        try:
            todos = self.coleccion.get(where={"usuario_id": usuario_final})

            total = len(todos["ids"]) if todos["ids"] else 0

            categorias = {}
            etiquetas = {}
            importancia_total = 0
            confianza_total = 0

            if todos["metadatas"]:
                for meta in todos["metadatas"]:
                    cat = meta.get("categoria", "sin_categoria")
                    categorias[cat] = categorias.get(cat, 0) + 1

                    etiquetas_str = meta.get("etiquetas_str", "")
                    if etiquetas_str:
                        for tag in etiquetas_str.split(","):
                            if tag:
                                etiquetas[tag] = etiquetas.get(tag, 0) + 1

                    importancia_total += meta.get("importancia", 5)
                    confianza_total += meta.get("confianza", 0.7)

            top_etiquetas = sorted(etiquetas.items(), key=lambda x: x[1], reverse=True)[
                :10
            ]

            return {
                "total_items": total,
                "categorias": categorias,
                "etiquetas": dict(top_etiquetas),
                "total_etiquetas_unicas": len(etiquetas),
                "importancia_promedio": (
                    round(importancia_total / total, 2) if total > 0 else 0
                ),
                "confianza_promedio": (
                    round(confianza_total / total, 2) if total > 0 else 0
                ),
                "usuario_id": usuario_final,
            }
        except Exception as e:
            print(f"⚠️ Error obteniendo estadísticas: {e}")
            return {
                "total_items": 0,
                "categorias": {},
                "etiquetas": {},
                "total_etiquetas_unicas": 0,
                "importancia_promedio": 0,
                "confianza_promedio": 0,
                "usuario_id": usuario_final,
            }

    def eliminar_item(self, id: str):
        """Elimina un item por su ID"""
        self.coleccion.delete(ids=[id])

    def eliminar_por_usuario(self, usuario_id: str) -> int:
        """Elimina todo el conocimiento de un usuario"""
        try:
            resultados = self.coleccion.get(where={"usuario_id": usuario_id})

            if resultados["ids"]:
                self.coleccion.delete(ids=resultados["ids"])
                return len(resultados["ids"])
            return 0
        except Exception as e:
            print(f"⚠️ Error eliminando por usuario: {e}")
            return 0

    def listar_usuarios_con_conocimiento(self) -> List[str]:
        """Lista todos los usuarios que tienen conocimiento guardado"""
        try:
            todos = self.coleccion.get()
            usuarios = set()
            if todos["metadatas"]:
                for meta in todos["metadatas"]:
                    uid = meta.get("usuario_id", "anonimo")
                    usuarios.add(uid)
            return list(usuarios)
        except:
            return []
