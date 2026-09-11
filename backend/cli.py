# ============================================
#  CLI PARA ASTRO-IA
#  Interfaz de terminal con colores
# ============================================

import sys
import os
from datetime import datetime
from ia_core import IACore


# Colores ANSI
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"


class CLI:
    def __init__(self):
        print(f"\n{Color.CYAN}{Color.BOLD}")
        print("╔══════════════════════════════════════╗")
        print("║        🧠  ASTRO-IA CLI              ║")
        print("║   Escribe 'help' para ver comandos  ║")
        print("╚══════════════════════════════════════╝")
        print(f"{Color.RESET}")

        self.ia = IACore()
        self.usuario = os.getenv("USER", "usuario")
        self.ia.set_usuario(self.usuario)

        print(f"{Color.GREEN}✅ Usuario: {Color.BOLD}{self.usuario}{Color.RESET}")
        print(
            f"{Color.DIM}   Escribe 'help' para ver comandos disponibles{Color.RESET}\n"
        )

    def run(self):
        """Loop principal"""
        while True:
            try:
                # Prompt
                mensaje = input(f"{Color.BLUE}{Color.BOLD}👤 Tú:{Color.RESET} ").strip()

                if not mensaje:
                    continue

                # Comandos especiales
                if mensaje.startswith("/") or mensaje.lower() in [
                    "exit",
                    "quit",
                    "salir",
                ]:
                    if self._procesar_comando(mensaje):
                        continue
                    else:
                        break

                # Procesar mensaje normal
                print(f"{Color.MAGENTA}🤖 IA:{Color.RESET} ", end="", flush=True)
                respuesta = self.ia.pensar(mensaje)
                print(f"{Color.GREEN}{respuesta}{Color.RESET}\n")

            except KeyboardInterrupt:
                print(f"\n\n{Color.YELLOW}👋 ¡Hasta luego!{Color.RESET}")
                break
            except Exception as e:
                print(f"{Color.RED}❌ Error: {e}{Color.RESET}\n")

    def _procesar_comando(self, comando: str) -> bool:
        """Procesa comandos especiales. Retorna False si debe salir."""
        cmd = comando.lower().lstrip("/")

        if cmd in ["exit", "quit", "salir"]:
            print(f"{Color.YELLOW}👋 ¡Hasta luego!{Color.RESET}")
            return False

        elif cmd == "help":
            self._mostrar_help()

        elif cmd == "reset":
            self.ia.historial_conversacion = []
            self.ia.memoria.corto_plazo.limpiar()
            print(f"{Color.GREEN}🔄 Conversación reiniciada{Color.RESET}\n")

        elif cmd == "stats":
            self._mostrar_stats()

        elif cmd == "memoria":
            self._mostrar_memoria()

        elif cmd.startswith("buscar "):
            termino = comando[7:].strip()
            self._buscar(termino)

        elif cmd.startswith("personalidad "):
            personalidad = comando[13:].strip()
            if personalidad in ["amigable", "profesional", "creativo", "sarcastico"]:
                self.ia.personalidad = personalidad
                print(f"{Color.GREEN}✅ Personalidad: {personalidad}{Color.RESET}\n")
            else:
                print(f"{Color.RED}❌ Personalidad no válida{Color.RESET}\n")

        elif cmd == "clear":
            os.system("clear" if os.name == "posix" else "cls")

        else:
            print(f"{Color.RED}❌ Comando no reconocido: {cmd}{Color.RESET}\n")
            return False

        return True

    def _mostrar_help(self):
        """Muestra la ayuda"""
        help_text = f"""
{Color.CYAN}{Color.BOLD}📖 COMANDOS DISPONIBLES{Color.RESET}

{Color.YELLOW}Comandos:{Color.RESET}
  {Color.GREEN}/help{Color.RESET}              - Mostrar esta ayuda
  {Color.GREEN}/reset{Color.RESET}             - Reiniciar conversación
  {Color.GREEN}/stats{Color.RESET}             - Ver estadísticas
  {Color.GREEN}/memoria{Color.RESET}           - Ver conocimiento guardado
  {Color.GREEN}/buscar <término>{Color.RESET}  - Buscar en el conocimiento
  {Color.GREEN}/personalidad <modo>{Color.RESET} - Cambiar personalidad
  {Color.GREEN}/clear{Color.RESET}             - Limpiar pantalla
  {Color.GREEN}/exit{Color.RESET}              - Salir

{Color.YELLOW}Personalidades:{Color.RESET}
  • amigable, profesional, creativo, sarcastico

{Color.YELLOW}Ejemplos:{Color.RESET}
  • "Me llamo Carlos y me gusta el rock"
  • "¿Qué recuerdas de mí?"
  • "Cuéntame un chiste"
"""
        print(help_text)

    def _mostrar_stats(self):
        """Muestra estadísticas"""
        try:
            stats = self.ia.ver_estadisticas()
            memoria = stats["memoria_dual"]
            largo = memoria["largo_plazo"]

            print(f"\n{Color.CYAN}{Color.BOLD}📊 ESTADÍSTICAS{Color.RESET}")
            print(f"{Color.YELLOW}👤 Usuario:{Color.RESET} {stats['usuario_actual']}")
            print(
                f"{Color.YELLOW}🎭 Personalidad:{Color.RESET} {stats['personalidad']}"
            )
            print(f"{Color.YELLOW}💬 Mensajes:{Color.RESET} {stats['total_mensajes']}")
            print(f"\n{Color.YELLOW}📚 Memoria largo plazo:{Color.RESET}")
            print(f"   Items: {largo['total_items']}")
            print(f"   Etiquetas: {largo['total_etiquetas_unicas']}")
            print(f"   Categorías: {len(largo['categorias'])}")
            print(f"\n{Color.YELLOW}💭 Memoria corto plazo:{Color.RESET}")
            print(f"   Items: {memoria['corto_plazo']['items_actuales']}")
            print()
        except Exception as e:
            print(f"{Color.RED}❌ Error: {e}{Color.RESET}\n")

    def _mostrar_memoria(self):
        """Muestra el conocimiento guardado"""
        try:
            items = self.ia.buscar("", n_resultados=20)
            if not items:
                print(
                    f"{Color.YELLOW}ℹ️ No hay conocimiento guardado aún{Color.RESET}\n"
                )
                return

            print(f"\n{Color.CYAN}{Color.BOLD}📚 CONOCIMIENTO GUARDADO{Color.RESET}")
            for i, item in enumerate(items, 1):
                categoria = item["metadata"].get("categoria", "general")
                importancia = item.get("importancia", 5)
                emoji = "🔴" if importancia >= 8 else "🟡" if importancia >= 5 else "🟢"
                print(f"{emoji} [{categoria}] {item['documento'][:100]}")
            print()
        except Exception as e:
            print(f"{Color.RED}❌ Error: {e}{Color.RESET}\n")

    def _buscar(self, termino: str):
        """Busca en el conocimiento"""
        try:
            items = self.ia.buscar(termino, n_resultados=5)
            if not items:
                print(f"{Color.YELLOW}ℹ️ No se encontró: {termino}{Color.RESET}\n")
                return

            print(f"\n{Color.CYAN}🔍 Resultados para '{termino}':{Color.RESET}")
            for i, item in enumerate(items, 1):
                similitud = item.get("similitud", 0)
                print(f"{Color.GREEN}{i}.{Color.RESET} {item['documento']}")
                print(f"   {Color.DIM}Similitud: {similitud:.2f}{Color.RESET}")
            print()
        except Exception as e:
            print(f"{Color.RED}❌ Error: {e}{Color.RESET}\n")


if __name__ == "__main__":
    cli = CLI()
    cli.run()
