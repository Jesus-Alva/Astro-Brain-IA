# ============================================
#  CORE DE LA IA CON SOPORTE MULTIUSUARIO
# ============================================

import ollama
from memoria_vectorial import MemoriaVectorial
from memoria_dual import MemoriaDual
from extractor import ExtractorInteligente
from usuario import Usuario
from feedback import Feedback
from utils import Utils
from typing import List, Dict
import json


class IACore:
    def __init__(self):
        self.config = Utils.cargar_config()

        # Memoria vectorial
        self.memoria_vectorial = MemoriaVectorial(
            directorio=self.config["memoria"]["directorio"], nombre_coleccion="astro_ia"
        )

        # Memoria dual
        self.memoria = MemoriaDual(self.memoria_vectorial)

        # Feedback
        self.feedback = Feedback(self.memoria_vectorial)

        # Extractor
        self.extractor = ExtractorInteligente(modelo=self.config["ia"]["modelo"])

        # Usuario
        self.gestor_usuarios = Usuario(self.config["memoria"]["directorio"])
        self.usuario_actual = None
        self.usuario_id_actual = "anonimo"  # ✅ NUEVO

        # Configuración
        self.modelo = self.config["ia"]["modelo"]
        self.temperatura = self.config["ia"]["temperatura"]
        self.nombre = self.config["ia"]["nombre"]
        self.personalidad = self.config["ia"]["modo_personalidad"]
        self.umbral_similitud = self.config["memoria"]["similaridad_minima"]

        self.historial_conversacion = []
        self.contador_mensajes = 0

        stats = self.memoria.obtener_estadisticas()
        print(f"\n🧠 {self.nombre} iniciada:")
        print(f"📚 {stats['largo_plazo']['total_items']} items en memoria largo plazo")
        print(
            f"💭 {stats['corto_plazo']['items_actuales']} items en memoria corto plazo"
        )
        print(
            f"👥 {len(self.memoria_vectorial.listar_usuarios_con_conocimiento())} usuarios con conocimiento"
        )

        try:
            stats_feedback = self.feedback.obtener_estadisticas()
            print(f"⭐ {stats_feedback['total_feedback']} feedbacks registrados")
        except Exception as e:
            print(f"⚠️ No se pudo cargar feedback: {e}")

    def set_usuario(self, usuario_id: str):
        """
        ✅ CAMBIA EL USUARIO ACTUAL.
        Esto aísla el conocimiento, historial y memoria de corto plazo.
        """
        if usuario_id == self.usuario_id_actual:
            return  # Ya está en ese usuario

        print(f"\n👤 Cambiando de usuario: {self.usuario_id_actual} → {usuario_id}")

        # Guardar lo pendiente del usuario anterior
        if self.usuario_id_actual != "anonimo":
            try:
                self.memoria.consolidar(forzar=True)
            except:
                pass

        # ✅ Cambiar usuario en todas las capas
        self.usuario_id_actual = usuario_id
        self.memoria.set_usuario(usuario_id)
        self.memoria_vectorial.set_usuario(usuario_id)

        # Cargar perfil si existe
        perfil = self.gestor_usuarios.cargar_usuario(usuario_id)
        if perfil:
            self.usuario_actual = perfil
            # Aplicar preferencias
            prefs = perfil.get("preferencias", {})
            if prefs.get("personalidad"):
                self.personalidad = prefs["personalidad"]
            if prefs.get("temperatura"):
                self.temperatura = prefs["temperatura"]

        # ✅ LIMPIAR HISTORIAL DE CONVERSACIÓN (aislamiento)
        self.historial_conversacion = []
        self.memoria.corto_plazo.limpiar()

        print(f"✅ Usuario cambiado a: {usuario_id}")
        print(
            f"📚 Items en memoria de este usuario: {self.memoria.obtener_estadisticas()['largo_plazo']['total_items']}"
        )

    def pensar(self, mensaje_usuario: str) -> str:
        """Procesa el mensaje y genera respuesta usando memoria dual DEL USUARIO ACTUAL"""
        self.contador_mensajes += 1

        self.memoria.agregar_mensaje(mensaje_usuario, "user")

        self.historial_conversacion.append(
            {
                "role": "user",
                "content": mensaje_usuario,
                "timestamp": Utils.formatear_fecha(),
            }
        )

        contexto_completo = self.memoria.obtener_contexto_completo(mensaje_usuario)
        contexto = self._construir_contexto(mensaje_usuario, contexto_completo)

        try:
            respuesta = ollama.chat(
                model=self.modelo,
                messages=[
                    {"role": "system", "content": contexto},
                    *self.historial_conversacion[-self.config["ia"]["max_contexto"] :],
                ],
                options={"temperature": self.temperatura},
            )

            texto_respuesta = respuesta["message"]["content"]

            self.memoria.agregar_mensaje(texto_respuesta, "assistant")

            self.historial_conversacion.append(
                {
                    "role": "assistant",
                    "content": texto_respuesta,
                    "timestamp": Utils.formatear_fecha(),
                }
            )

            if self.contador_mensajes % 4 == 0:
                self._aprender_automaticamente()

            if self.contador_mensajes % 10 == 0:
                resultado = self.memoria.consolidar()
                if resultado.get("consolidado"):
                    print(
                        f"🧠 Consolidación: {resultado['items_consolidados']} items para {self.usuario_id_actual}"
                    )

            return texto_respuesta

        except Exception as e:
            return f"❌ Error: {e}"

    def _construir_contexto(self, mensaje: str, contexto_completo: Dict) -> str:
        """Construye contexto con memoria dual + feedback + usuario"""
        personalidades = {
            "amigable": "responde de manera cálida, cercana y con emojis ocasionales",
            "profesional": "responde de manera formal, precisa y estructurada",
            "creativo": "responde de manera original y con analogías",
            "sarcastico": "responde con humor irónico",
        }

        estilo = personalidades.get(self.personalidad, personalidades["amigable"])

        consejos_feedback = ""
        if hasattr(self, "feedback") and self.feedback:
            try:
                consejos_feedback = self.feedback.obtener_consejos(mensaje, n=2)
            except:
                pass

        conversacion_reciente = contexto_completo.get("conversacion_reciente", [])
        texto_conversacion = ""
        if conversacion_reciente:
            texto_conversacion = "\nCONVERSACIÓN RECIENTE:\n"
            for item in conversacion_reciente[-5:]:
                rol = item["metadata"].get("role", "sistema")
                texto_conversacion += f"- [{rol}]: {item['contenido'][:150]}\n"

        conocimiento_relevante = contexto_completo.get("conocimiento_relevante", [])
        texto_conocimiento = ""
        if conocimiento_relevante:
            texto_conocimiento = (
                f"\nCONOCIMIENTO SOBRE {self.usuario_id_actual.upper()}:\n"
            )
            for idx, item in enumerate(conocimiento_relevante, 1):
                categoria = item["metadata"].get("categoria", "general")
                texto_conocimiento += f"{idx}. [{categoria}] {item['documento']}\n"

        hechos_sesion = contexto_completo.get("hechos_sesion", [])
        texto_hechos = ""
        if hechos_sesion:
            texto_hechos = "\nHECHOS DE ESTA SESIÓN:\n"
            for hecho in hechos_sesion[-3:]:
                texto_hechos += f"- {hecho['contenido']}\n"

        return f"""
        Eres {self.nombre}, una IA personal con memoria dual y soporte multiusuario.
        
        USUARIO ACTUAL: {self.usuario_id_actual}
        PERSONALIDAD: {estilo}
        
        {texto_conversacion}
        
        {texto_conocimiento}
        
        {texto_hechos}
        
        {consejos_feedback}
        
        INSTRUCCIONES:
        1. ✅ SOLO usa el conocimiento del usuario actual ({self.usuario_id_actual})
        2. NUNCA mezcles información de otros usuarios
        3. Si no sabes algo del usuario, di que no lo sabes aún
        4. Mantén continuidad con la conversación reciente
        5. Usa los consejos del feedback si están disponibles
        
        Pregunta del usuario: {mensaje}
        """

    def _aprender_automaticamente(self):
        """Aprendizaje automático CON usuario_id"""
        if len(self.historial_conversacion) < 2:
            return

        mensajes_recientes = self.historial_conversacion[-4:]

        try:
            print(f"\n🧠 Extrayendo conocimiento para {self.usuario_id_actual}...")
            extraccion = self.extractor.extraer_conocimiento(mensajes_recientes)

            items = extraccion.get("items", [])
            if not items:
                print("   ℹ️ No se encontró información nueva")
                return

            items_priorizados = self.extractor.priorizar_conocimiento(items)

            for item in items_priorizados:
                self.memoria.agregar_hecho(
                    hecho=item["texto"],
                    categoria=item["categoria"],
                    etiquetas=item["etiquetas"],
                )

                emoji = (
                    "🔴"
                    if item["importancia"] >= 8
                    else "🟡" if item["importancia"] >= 5 else "🟢"
                )
                print(f"   {emoji} [{item['categoria']}] {item['texto'][:60]}...")

            print(
                f"\n✅ {len(items_priorizados)} items guardados para {self.usuario_id_actual}"
            )

        except Exception as e:
            print(f"⚠️ Error en aprendizaje automático: {e}")

    def aprender_manual(self) -> Dict:
        """Aprendizaje manual CON usuario_id"""
        if len(self.historial_conversacion) < 2:
            return {"error": "Conversación muy corta"}

        try:
            extraccion = self.extractor.extraer_conocimiento(
                self.historial_conversacion
            )
            items = extraccion.get("items", [])
            items_priorizados = self.extractor.priorizar_conocimiento(items)

            guardados = []
            for item in items_priorizados:
                id_item = self.memoria.largo_plazo.guardar(
                    contenido=item["texto"],
                    categoria=item["categoria"],
                    etiquetas=item["etiquetas"],
                    importancia=item["importancia"],
                    confianza=item["confianza"],
                    usuario_id=self.usuario_id_actual,  # ✅ AISLAMIENTO
                    metadata={"tipo": "aprendizaje_manual"},
                )
                guardados.append({**item, "id": id_item})

            return {
                "items_guardados": len(guardados),
                "usuario_id": self.usuario_id_actual,
                "items": guardados,
                "resumen": extraccion.get("resumen", "Sin resumen"),
            }
        except Exception as e:
            return {"error": str(e)}

    def consolidar_memoria(self, forzar: bool = True) -> Dict:
        return self.memoria.consolidar(forzar=forzar)

    def olvidar(self, criterio: str, valor, dry_run: bool = True) -> Dict:
        return self.memoria.olvidar(criterio, valor, dry_run)

    def resumen_sesion(self) -> Dict:
        return self.memoria.resumen_sesion()

    def buscar(self, consulta: str, n_resultados: int = 5) -> List[Dict]:
        return self.memoria.largo_plazo.buscar(
            consulta, n_resultados, usuario_id=self.usuario_id_actual
        )

    def buscar_por_categoria(self, categoria: str) -> List[Dict]:
        return self.memoria.largo_plazo.buscar_por_categoria(
            categoria, usuario_id=self.usuario_id_actual
        )

    def buscar_por_etiqueta(self, etiqueta: str) -> List[Dict]:
        return self.memoria.largo_plazo.buscar_por_etiqueta(
            etiqueta, usuario_id=self.usuario_id_actual
        )

    def ver_estadisticas(self) -> Dict:
        return {
            "memoria_dual": self.memoria.obtener_estadisticas(),
            "usuario_actual": self.usuario_id_actual,
            "personalidad": self.personalidad,
            "total_mensajes": self.contador_mensajes,
        }
