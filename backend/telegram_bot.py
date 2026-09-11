# ============================================
#  BOT DE TELEGRAM PARA ASTRO-IA
# ============================================

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from ia_core import IACore

# Configurar logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Token del bot (desde variable de entorno)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")

# Instancia global de la IA
ia = IACore()


# ============================================
#  COMANDOS
# ============================================


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    usuario = update.effective_user.first_name or "Usuario"
    user_id = str(update.effective_user.id)

    # Cambiar usuario en la IA (aislamiento por Telegram user_id)
    ia.set_usuario(f"tg_{user_id}")

    mensaje = f"""
🧠 ¡Hola {usuario}!

Soy **Astro-IA**, tu asistente personal con memoria continua.

*Comandos disponibles:*
/start - Iniciar conversación
/help - Ver ayuda
/reset - Reiniciar conversación
/stats - Ver estadísticas
/personalidad - Cambiar personalidad

*Ejemplos de uso:*
• "Me llamo {usuario}"
• "¿Qué recuerdas de mí?"
• "Cuéntame un chiste"

¡Empieza a escribir cuando quieras! 🚀
    """
    await update.message.reply_text(mensaje, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    mensaje = """
📖 *AYUDA DE ASTRO-IA*

*Comandos:*
/start - Iniciar
/help - Esta ayuda
/reset - Reiniciar conversación
/stats - Ver estadísticas
/personalidad - Cambiar personalidad
/olvidar - Olvidar información específica

*Consejos:*
• Cuéntame cosas sobre ti y las recordaré
• Puedo recordar conversaciones anteriores
• Usa 👍/👎 para darme feedback

*Ejemplos:*
• "Me llamo Carlos y me gusta el rock"
• "¿Qué música me gusta?"
• "Estoy trabajando en un proyecto de IA"
    """
    await update.message.reply_text(mensaje, parse_mode="Markdown")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /reset - Reinicia la conversación"""
    ia.historial_conversacion = []
    ia.memoria.corto_plazo.limpiar()
    await update.message.reply_text(
        "🔄 Conversación reiniciada.\n"
        "Tu conocimiento a largo plazo se mantiene intacto."
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats - Ver estadísticas"""
    try:
        stats = ia.ver_estadisticas()
        memoria = stats["memoria_dual"]
        largo = memoria["largo_plazo"]

        mensaje = f"""
📊 *TUS ESTADÍSTICAS*

👤 Usuario: `{stats['usuario_actual']}`
🎭 Personalidad: {stats['personalidad']}
💬 Mensajes: {stats['total_mensajes']}

*Memoria:*
📚 Items largo plazo: {largo['total_items']}
🏷️ Etiquetas únicas: {largo['total_etiquetas_unicas']}
📂 Categorías: {len(largo['categorias'])}

*Sesión actual:*
💭 Items en corto plazo: {memoria['corto_plazo']['items_actuales']}
    """
        await update.message.reply_text(mensaje, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def personalidad_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /personalidad - Cambiar personalidad"""
    keyboard = [
        [InlineKeyboardButton("😊 Amigable", callback_data="person_amigable")],
        [InlineKeyboardButton("💼 Profesional", callback_data="person_profesional")],
        [InlineKeyboardButton("🎨 Creativo", callback_data="person_creativo")],
        [InlineKeyboardButton("😏 Sarcástico", callback_data="person_sarcastico")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎭 Elige tu personalidad preferida:",
        reply_markup=reply_markup,
    )


async def olvidar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /olvidar - Olvido selectivo"""
    argumentos = context.args
    if not argumentos:
        await update.message.reply_text(
            "📝 Uso: `/olvidar categoria opiniones`\n"
            "o `/olvidar etiqueta temporal`\n"
            "o `/olvidar importancia_menor_a 3`",
            parse_mode="Markdown",
        )
        return

    criterio = argumentos[0]
    valor = argumentos[1] if len(argumentos) > 1 else ""

    try:
        # Convertir valor si es necesario
        if criterio in ["importancia_menor_a", "antiguo_mas_de_dias"]:
            valor = int(valor)
        elif criterio == "confianza_menor_a":
            valor = float(valor)

        # Simular primero
        simulacion = ia.olvidar(criterio, valor, dry_run=True)

        if simulacion.get("eliminaria", 0) == 0:
            await update.message.reply_text(
                f"ℹ️ No hay items que cumplan: {criterio}={valor}"
            )
            return

        # Confirmar
        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Sí, olvidar",
                    callback_data=f"olvidar_confirm_{criterio}_{valor}",
                ),
                InlineKeyboardButton("❌ Cancelar", callback_data="olvidar_cancel"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"⚠️ Se eliminarán *{simulacion['eliminaria']}* items.\n" f"¿Estás seguro?",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


# ============================================
#  MANEJADORES DE MENSAJES
# ============================================


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los mensajes de texto"""
    user_id = str(update.effective_user.id)
    mensaje = update.message.text

    # Cambiar usuario
    ia.set_usuario(f"tg_{user_id}")

    # Mostrar "escribiendo..."
    await update.message.chat.send_action(action="typing")

    try:
        # Obtener respuesta
        respuesta = ia.pensar(mensaje)

        # Enviar respuesta con botones de feedback
        keyboard = [
            [
                InlineKeyboardButton(
                    "👍", callback_data=f"fb_pos_{hash(mensaje) % 10000}"
                ),
                InlineKeyboardButton(
                    "👎", callback_data=f"fb_neg_{hash(mensaje) % 10000}"
                ),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Guardar mensaje para feedback
        if not hasattr(context, "user_data"):
            context.user_data = {}
        context.user_data["ultimo_mensaje"] = mensaje
        context.user_data["ultima_respuesta"] = respuesta

        await update.message.reply_text(
            respuesta,
            reply_markup=reply_markup,
        )
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        await update.message.reply_text(
            "❌ Lo siento, tuve un problema procesando tu mensaje."
        )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los botones inline"""
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = str(query.from_user.id)

    # --- Feedback ---
    if data.startswith("fb_"):
        tipo = data.split("_")[1]
        es_positivo = tipo == "pos"

        try:
            ia.set_usuario(f"tg_{user_id}")
            mensaje = context.user_data.get("ultimo_mensaje", "")
            respuesta = context.user_data.get("ultima_respuesta", "")

            if hasattr(ia, "feedback") and ia.feedback:
                ia.feedback.registrar_feedback(
                    mensaje=mensaje,
                    respuesta=respuesta,
                    es_positivo=es_positivo,
                    usuario=f"tg_{user_id}",
                )

            emoji = "👍" if es_positivo else "👎"
            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text(f"{emoji} ¡Gracias por tu feedback!")
        except Exception as e:
            await query.message.reply_text(f"❌ Error: {e}")

    # --- Personalidad ---
    elif data.startswith("person_"):
        personalidad = data.replace("person_", "")
        ia.personalidad = personalidad
        ia.set_usuario(f"tg_{user_id}")

        emoji = {
            "amigable": "😊",
            "profesional": "💼",
            "creativo": "🎨",
            "sarcastico": "😏",
        }.get(personalidad, "🎭")

        await query.edit_message_text(
            f"✅ Personalidad cambiada a: {emoji} {personalidad.capitalize()}"
        )

    # --- Olvido ---
    elif data.startswith("olvidar_confirm_"):
        try:
            partes = data.replace("olvidar_confirm_", "").split("_", 1)
            criterio = partes[0]
            valor = partes[1]

            if criterio in ["importancia_menor_a", "antiguo_mas_de_dias"]:
                valor = int(valor)
            elif criterio == "confianza_menor_a":
                valor = float(valor)

            ia.set_usuario(f"tg_{user_id}")
            resultado = ia.olvidar(criterio, valor, dry_run=False)

            await query.edit_message_text(
                f"✅ Eliminados: {resultado.get('eliminados', 0)} items"
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {e}")

    elif data == "olvidar_cancel":
        await query.edit_message_text("❌ Operación cancelada")


# ============================================
#  MAIN
# ============================================


def main():
    """Inicia el bot"""
    if not TELEGRAM_TOKEN:
        print("❌ ERROR: TELEGRAM_TOKEN no está configurado")
        print("📝 Configúralo con: export TELEGRAM_TOKEN='tu_token_aqui'")
        return

    print("🤖 Iniciando bot de Telegram...")

    # Crear aplicación
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Añadir handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("personalidad", personalidad_command))
    application.add_handler(CommandHandler("olvidar", olvidar_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("✅ Bot iniciado. Presiona Ctrl+C para detener.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
