# message_components/achievements.py
# Sistema de logros y reconocimientos

import json
import database as db
from whatsapp_utils import responder_mensaje
from utils.formatters import formatear_logro_desbloqueado
from config import LOGROS_DISPONIBLES

def verificar_y_otorgar_logros(numero_remitente, usuario):
    """
    Verifica si el usuario ha desbloqueado nuevos logros.
    Retorna lista de logros nuevos desbloqueados.
    """
    logros_actuales = json.loads(usuario.get("logros_desbloqueados", "[]"))
    nuevos_logros = []

    # Obtener stats del usuario
    retos_completados = usuario.get("retos_completados", 0)
    racha_dias = usuario.get("racha_dias", 0)
    retos_sin_pistas = usuario.get("retos_sin_pistas", 0)
    progreso_temas = json.loads(usuario.get("progreso_temas", "{}"))

    # Verificar cada logro
    for logro_id, logro_data in LOGROS_DISPONIBLES.items():
        # Si ya lo tiene, skip
        if logro_id in logros_actuales:
            continue

        # Si no tiene requisitos (como primer_paso), skip
        if "requisito" not in logro_data:
            continue

        requisito = logro_data["requisito"]
        cumple_requisito = True

        # Verificar requisitos
        if "retos_completados" in requisito:
            if retos_completados < requisito["retos_completados"]:
                cumple_requisito = False

        if "racha_dias" in requisito:
            if racha_dias < requisito["racha_dias"]:
                cumple_requisito = False

        if "retos_sin_pistas" in requisito:
            if retos_sin_pistas < requisito["retos_sin_pistas"]:
                cumple_requisito = False

        if "tema" in requisito and "nivel" in requisito:
            tema = requisito["tema"]
            nivel_req = requisito["nivel"]
            if tema not in progreso_temas or progreso_temas[tema].get("nivel", 1) < nivel_req:
                cumple_requisito = False

        # Si cumple, otorgar logro
        if cumple_requisito:
            logros_actuales.append(logro_id)
            nuevos_logros.append(logro_data)

    # Actualizar logros si hay nuevos
    if nuevos_logros:
        db.actualizar_usuario(numero_remitente, {
            "logros_desbloqueados": json.dumps(logros_actuales)
        })

        # Notificar cada logro
        for logro in nuevos_logros:
            mensaje = formatear_logro_desbloqueado(
                logro["nombre"],
                logro["descripcion"],
                logro["emoji"]
            )
            responder_mensaje(numero_remitente, mensaje, [])

            # Bonus de puntos
            if "puntos_bonus" in logro:
                puntos_actuales = usuario.get("puntos", 0)
                db.actualizar_usuario(numero_remitente, {
                    "puntos": puntos_actuales + logro["puntos_bonus"]
                })

    return nuevos_logros


def mostrar_logros_usuario(numero_remitente, usuario):
    """
    Muestra todos los logros del usuario (desbloqueados y bloqueados).
    """
    logros_desbloqueados = json.loads(usuario.get("logros_desbloqueados", "[]"))

    mensaje = f"🏆 *TUS LOGROS*\n\n"
    mensaje += f"*DESBLOQUEADOS:* ✅\n\n"

    # Logros desbloqueados
    if logros_desbloqueados:
        for logro_id in logros_desbloqueados:
            if logro_id in LOGROS_DISPONIBLES:
                logro = LOGROS_DISPONIBLES[logro_id]
                mensaje += f"{logro['emoji']} *{logro['nombre']}*\n"
                mensaje += f"   {logro['descripcion']}\n\n"
    else:
        mensaje += "Aún no has desbloqueado logros 🎯\n\n"

    mensaje += f"\n*BLOQUEADOS:* 🔒\n\n"

    # Logros bloqueados
    for logro_id, logro in LOGROS_DISPONIBLES.items():
        if logro_id not in logros_desbloqueados and "requisito" in logro:
            mensaje += f"🔒 *{logro['nombre']}*\n"
            mensaje += f"   {logro['descripcion']}\n\n"

    responder_mensaje(numero_remitente, mensaje, [])

