# utils/formatters.py
# Funciones para formatear mensajes de WhatsApp de forma atractiva

from src.utils.emojis import *

def generar_barra_progreso(actual, total, longitud=10):
    """
    Genera una barra de progreso visual.

    Ejemplo: ██████░░░░ 60%
    """
    if total == 0:
        porcentaje = 0
    else:
        porcentaje = int((actual / total) * 100)

    bloques_llenos = int((actual / total) * longitud) if total > 0 else 0
    bloques_vacios = longitud - bloques_llenos

    barra = "█" * bloques_llenos + "░" * bloques_vacios
    return f"{barra} {porcentaje}%"


def formatear_puntos_ganados(puntos_base, bonus_racha=0, contexto="reto"):
    """
    Formatea un mensaje de puntos ganados de forma visual.

    Args:
        puntos_base: Puntos base del reto/actividad
        bonus_racha: Bonus por racha de días
        contexto: 'reto', 'logro', etc.
    """
    total = puntos_base + bonus_racha

    mensaje = f"{CORRECTO} ¡CORRECTO!\n\n"
    mensaje += "━━━━━━━━━━━━\n"
    mensaje += f"{RETO} Reto: +{puntos_base}\n"

    if bonus_racha > 0:
        mensaje += f"{RACHA} Racha: +{bonus_racha}\n"

    mensaje += "━━━━━━━━━━━━\n"
    mensaje += f"{ESTRELLA} Total: +{total} pts"

    return mensaje


def formatear_nivel_up(nivel_nuevo, nombre_nivel=None):
    """
    Genera un mensaje de celebración por subir de nivel.
    """
    mensaje = f"\n{CELEBRACION}{COHETE}{CELEBRACION}{COHETE}{CELEBRACION}\n\n"
    mensaje += "┏━━━━━━━━━━━━━┓\n"
    mensaje += "┃  ¡NIVEL UP!  ┃\n"
    mensaje += f"┃   {NIVEL_UP} → {nivel_nuevo} {NIVEL_UP}   ┃\n"
    mensaje += "┗━━━━━━━━━━━━━┛\n\n"

    if nombre_nivel:
        mensaje += f"Ahora eres *{nombre_nivel}* {TROFEO}\n"

    mensaje += f"\n{COHETE}{CELEBRACION}{COHETE}{CELEBRACION}{COHETE}"

    return mensaje


def formatear_logro_desbloqueado(nombre_logro, descripcion, emoji=LOGRO):
    """
    Formatea un mensaje de logro desbloqueado.
    """
    mensaje = f"\n{CELEBRACION} ¡LOGRO DESBLOQUEADO! {CELEBRACION}\n\n"
    mensaje += f"{emoji} *{nombre_logro}*\n"
    mensaje += f"{descripcion}\n"

    return mensaje


def formatear_perfil_compacto(usuario_data):
    """
    Genera una versión compacta del perfil del usuario.
    """
    nombre = usuario_data.get('nombre', 'Estudiante')
    nivel = usuario_data.get('nivel', 1)
    puntos = usuario_data.get('puntos', 0)
    racha = usuario_data.get('racha_dias', 0)

    mensaje = f"{PERFIL} *{nombre}*\n"
    mensaje += f"{NIVEL_UP} Nivel {nivel} | "
    mensaje += f"{ESTRELLA} {puntos} pts | "
    mensaje += f"{RACHA} {racha} días\n"

    return mensaje


def formatear_error_con_pista(intento_numero, max_intentos=3):
    """
    Formatea un mensaje de error sugiriendo ayuda.
    """
    mensaje = f"{INCORRECTO} Incorrecto\n\n"

    if intento_numero == 1:
        mensaje += "¡No te rindas! Intenta de nuevo {PRACTICA}"
    elif intento_numero == 2:
        mensaje += f"{IDEA} ¿Necesitas una pista?\nEscribe *'pista'* si quieres ayuda"
    else:
        mensaje += f"{LIBRO} Este reto es difícil.\n"
        mensaje += "Escribe *'explicar'* para ver la teoría"

    return mensaje


def formatear_progreso_tema(tema, puntos, nivel, puntos_necesarios):
    """
    Muestra el progreso en un tema específico.
    """
    barra = generar_barra_progreso(puntos, puntos_necesarios, 10)

    mensaje = f"{CONCEPTO} *{tema}*\n"
    mensaje += f"Nivel {nivel}\n"
    mensaje += f"{barra}\n"
    mensaje += f"{puntos}/{puntos_necesarios} pts\n"

    return mensaje


def separador(estilo="simple"):
    """
    Genera un separador visual.
    """
    if estilo == "simple":
        return "━━━━━━━━━━━━"
    elif estilo == "doble":
        return "═══════════════"
    elif estilo == "puntos":
        return "• • • • • • • • •"
    else:
        return "─────────────"


def formatear_menu_ayuda():
    """
    Genera el menú de ayuda contextual.
    """
    mensaje = f"\n{separador('puntos')}\n"
    mensaje += f"{MENU} *Comandos útiles:*\n"
    mensaje += f"• *menu* - Ver opciones\n"
    mensaje += f"• *perfil* - Tu progreso\n"
    mensaje += f"• *ayuda* - Pedir pista\n"
    mensaje += f"{separador('puntos')}\n"

    return mensaje


def chunk_mensaje(texto, max_length=1000):
    """
    Divide un mensaje largo en chunks para WhatsApp.
    """
    if len(texto) <= max_length:
        return [texto]

    chunks = []
    palabras = texto.split()
    chunk_actual = ""

    for palabra in palabras:
        if len(chunk_actual) + len(palabra) + 1 <= max_length:
            chunk_actual += palabra + " "
        else:
            chunks.append(chunk_actual.strip())
            chunk_actual = palabra + " "

    if chunk_actual:
        chunks.append(chunk_actual.strip())

    return chunks

