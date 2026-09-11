# ============================================
#  BOT DE WHATSAPP PARA ASTRO-IA (TWILIO)
# ============================================

import os
import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from ia_core import IACore

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Credenciales de Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# Cliente de Twilio (para enviar mensajes proactivos)
twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    except Exception as e:
        logger.error(f"Error inicializando Twilio: {e}")

# Instancia global de la IA
ia = IACore()

# Mapeo de números a usuarios
# { "whatsapp:+521234567890": "usuario_nombre" }
usuarios_whatsapp = {}

app = FastAPI(title="Astro-IA WhatsApp Bot")


# ============================================
#  UTILIDADES
# ============================================


def obtener_usuario(numero: str) -> str:
    """Obtiene o crea un usuario a partir del número de WhatsApp"""
    if numero not in usuarios_whatsapp:
        # Crear ID de usuario basado en el número
        user_id = f"wa_{numero.replace('whatsapp:', '').replace('+', '')}"
        usuarios_whatsapp[numero] = user_id
        logger.info(f"👤 Nuevo usuario WhatsApp: {user_id}")
    return usuarios_whatsapp[numero]


def enviar_mensaje(numero: str, mensaje: str) -> bool:
    """Envía un mensaje proactivo por WhatsApp"""
    if not twilio_client:
        logger.error("Twilio no está configurado")
        return False

    try:
        twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=numero,
            body=mensaje,
        )
        return True
    except Exception as e:
        logger.error(f"Error enviando mensaje: {e}")
        return False


# ============================================
#  WEBHOOK
# ============================================


@app.post("/whatsapp/webhook")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    ProfileName: Optional[str] = Form(None),
):
    """
    Webhook que recibe los mensajes de WhatsApp.
    Twilio envía los mensajes aquí.
    """
    logger.info(f"📩 Mensaje de {From} ({ProfileName}): {Body[:50]}...")

    # Obtener/crear usuario
    usuario_id = obtener_usuario(From)
    ia.set_usuario(usuario_id)

    # Crear respuesta TwiML
    respuesta_twiml = MessagingResponse()

    # Procesar comandos
    mensaje = Body.strip()
    comando = mensaje.lower()

    try:
        # --- Comandos ---
        if comando in ["hola", "hi", "hello", "start", "iniciar"]:
            respuesta_twiml.message(
                f"🧠 ¡Hola {ProfileName or 'Usuario'}!\n\n"
                "Soy Astro-IA, tu asistente personal.\n\n"
                "*Comandos disponibles:*\n"
                "• *ayuda* - Ver ayuda\n"
                "• *reset* - Reiniciar conversación\n"
                "• *stats* - Ver estadísticas\n"
                "• *personalidad* - Cambiar personalidad\n"
                "• *olvidar* - Olvido selectivo\n\n"
                "¡Empieza a escribir cuando quieras!"
            )

        elif comando == "ayuda" or comando == "help":
            respuesta_twiml.message(
                "📖 *AYUDA DE ASTRO-IA*\n\n"
                "*Comandos:*\n"
                "• *reset* - Reiniciar conversación\n"
                "• *stats* - Ver estadísticas\n"
                "• *personalidad* - Cambiar personalidad\n"
                "• *olvidar* - Olvido selectivo\n\n"
                "*Consejos:*\n"
                "• Cuéntame cosas sobre ti y las recordaré\n"
                "• Puedo recordar conversaciones anteriores\n"
                "• Puedo cambiar mi personalidad\n\n"
                "*Ejemplos:*\n"
                '• "Me llamo Carlos y me gusta el rock"\n'
                '• "¿Qué música me gusta?"'
            )

        elif comando == "reset":
            ia.historial_conversacion = []
            ia.memoria.corto_plazo.limpiar()
            respuesta_twiml.message(
                "🔄 Conversación reiniciada.\n"
                "Tu conocimiento a largo plazo se mantiene."
            )

        elif comando == "stats":
            stats = ia.ver_estadisticas()
            memoria = stats["memoria_dual"]
            largo = memoria["largo_plazo"]

            respuesta_twiml.message(
                f"📊 *TUS ESTADÍSTICAS*\n\n"
                f"👤 Usuario: {stats['usuario_actual']}\n"
                f"🎭 Personalidad: {stats['personalidad']}\n"
                f"💬 Mensajes: {stats['total_mensajes']}\n\n"
                f"*Memoria:*\n"
                f"📚 Items: {largo['total_items']}\n"
                f"🏷️ Etiquetas: {largo['total_etiquetas_unicas']}\n"
                f"📂 Categorías: {len(largo['categorias'])}"
            )

        elif comando.startswith("personalidad"):
            partes = mensaje.split(maxsplit=1)
            if len(partes) > 1:
                personalidad = partes[1].lower().strip()
                if personalidad in [
                    "amigable",
                    "profesional",
                    "creativo",
                    "sarcastico",
                ]:
                    ia.personalidad = personalidad
                    emoji = {
                        "amigable": "😊",
                        "profesional": "💼",
                        "creativo": "🎨",
                        "sarcastico": "😏",
                    }.get(personalidad, "🎭")
                    respuesta_twiml.message(
                        f"✅ Personalidad cambiada a: {emoji} {personalidad.capitalize()}"
                    )
                else:
                    respuesta_twiml.message(
                        "❌ Personalidad no válida.\n"
                        "Opciones: amigable, profesional, creativo, sarcastico"
                    )
            else:
                respuesta_twiml.message(
                    "🎭 *Personalidades disponibles:*\n"
                    "• amigable 😊\n"
                    "• profesional 💼\n"
                    "• creativo 🎨\n"
                    "• sarcastico 😏\n\n"
                    "Uso: *personalidad amigable*"
                )

        elif comando.startswith("olvidar"):
            partes = mensaje.split()
            if len(partes) >= 3:
                criterio = partes[1]
                valor = partes[2]

                try:
                    if criterio in ["importancia_menor_a", "antiguo_mas_de_dias"]:
                        valor = int(valor)
                    elif criterio == "confianza_menor_a":
                        valor = float(valor)

                    resultado = ia.olvidar(criterio, valor, dry_run=False)
                    respuesta_twiml.message(
                        f"✅ Eliminados: {resultado.get('eliminados', 0)} items"
                    )
                except Exception as e:
                    respuesta_twiml.message(f"❌ Error: {e}")
            else:
                respuesta_twiml.message(
                    "📝 *Uso:*\n"
                    "• olvidar categoria opiniones\n"
                    "• olvidar etiqueta temporal\n"
                    "• olvidar importancia_menor_a 3"
                )

        # --- Mensaje normal ---
        else:
            # Generar respuesta con la IA
            respuesta = ia.pensar(mensaje)

            # Dividir si es muy larga (WhatsApp tiene límite de 1600 caracteres)
            if len(respuesta) > 1500:
                partes = [
                    respuesta[i : i + 1500] for i in range(0, len(respuesta), 1500)
                ]
                for parte in partes:
                    respuesta_twiml.message(parte)
            else:
                respuesta_twiml.message(respuesta)

    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        respuesta_twiml.message(
            "❌ Lo siento, tuve un problema procesando tu mensaje.\n"
            "Intenta de nuevo en unos segundos."
        )

    # Devolver TwiML
    return PlainTextResponse(
        content=str(respuesta_twiml),
        media_type="application/xml",
    )


# ============================================
#  ENDPOINTS ADICIONALES
# ============================================


@app.get("/whatsapp/health")
def health_check():
    """Verifica que el servicio está corriendo"""
    return {
        "status": "ok",
        "servicio": "WhatsApp Bot",
        "twilio_configurado": bool(twilio_client),
        "usuarios_activos": len(usuarios_whatsapp),
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/whatsapp/enviar")
def enviar_mensaje_manual(numero: str, mensaje: str):
    """Endpoint para enviar mensajes proactivos"""
    exito = enviar_mensaje(numero, mensaje)
    if exito:
        return {"enviado": True, "numero": numero}
    raise HTTPException(status_code=500, detail="Error enviando mensaje")


@app.get("/whatsapp/usuarios")
def listar_usuarios():
    """Lista los usuarios de WhatsApp registrados"""
    return {
        "total": len(usuarios_whatsapp),
        "usuarios": [
            {"numero": num, "id": uid} for num, uid in usuarios_whatsapp.items()
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)


# Middleware para saltar la advertencia de ngrok
class NgrokSkipMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Si la petición viene de ngrok y no tiene el header, añadirlo
        if "ngrok-skip-browser-warning" not in request.headers:
            # Crear una copia de los headers con el header añadido
            headers = dict(request.headers)
            headers["ngrok-skip-browser-warning"] = "true"
            # Reconstruir la petición con los nuevos headers
            request._headers = headers

        response = await call_next(request)
        return response


app.add_middleware(NgrokSkipMiddleware)
