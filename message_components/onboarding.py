# message_components/onboarding.py
# Sistema de onboarding personalizado

import time
import json
from config import LOGROS_DISPONIBLES
from utils.formatters import formatear_logro_desbloqueado
from utils.emojis import *
from whatsapp_utils import enviar_botones_basicos, responder_mensaje, enviar_menu_interactivo
import database as db

def iniciar_onboarding(numero_remitente, nombre_usuario):
    """
    Inicia el flujo de onboarding para nuevos usuarios.
    """
    # Mensaje 1: Bienvenida personalizada
    mensaje_bienvenida = f"¡Hola {nombre_usuario}! {ROBOT}\n\nSoy LogicBot {CODIGO}\nTu tutor personal de Java"
    responder_mensaje(numero_remitente, mensaje_bienvenida, [])

    time.sleep(1)

    # Mensaje 2: Propuesta
    mensaje_propuesta = f"{PREGUNTA} Antes de empezar...\n\nVoy a hacerte 2 preguntas rápidas para personalizar tu experiencia {ESTRELLA}"
    botones = [{"id": "onboarding_empezar", "title": f"Empezar {COHETE}"}]
    enviar_botones_basicos(numero_remitente, mensaje_propuesta, botones)

    # Actualizar estado
    db.actualizar_usuario(numero_remitente, {"estado_conversacion": "onboarding_paso_1"})


def handle_onboarding_paso_1(numero_remitente):
    """
    Pregunta 1: Nivel de experiencia.
    """
    mensaje = f"{PREGUNTA} ¿Has programado en Java antes?"
    botones = [
        {"id": "nivel_principiante", "title": f"Nunca {FACIL}"},
        {"id": "nivel_intermedio", "title": f"Un poco {INTERMEDIO}"},
        {"id": "nivel_avanzado", "title": f"Bastante {COHETE}"}
    ]
    enviar_botones_basicos(numero_remitente, mensaje, botones)


def handle_onboarding_paso_2(numero_remitente, nivel_seleccionado):
    """
    Pregunta 2: Preferencia de aprendizaje.
    """
    # Guardar nivel inicial
    db.actualizar_usuario(numero_remitente, {
        "nivel_inicial": nivel_seleccionado,
        "estado_conversacion": "onboarding_paso_2"
    })

    mensaje = f"{PREGUNTA} ¿Qué prefieres hacer?"
    botones = [
        {"id": "pref_curso", "title": f"Aprender desde cero {LIBRO}"},
        {"id": "pref_retos", "title": f"Practicar con retos {PRACTICA}"},
        {"id": "pref_ambos", "title": f"Ambas cosas {ESTRELLA}"}
    ]
    enviar_botones_basicos(numero_remitente, mensaje, botones)


def completar_onboarding(numero_remitente, preferencia):
    """
    Completa el onboarding y muestra el tutorial rápido.
    """
    # Guardar preferencia
    db.actualizar_usuario(numero_remitente, {
        "preferencia_aprendizaje": preferencia,
        "estado_conversacion": "onboarding_tutorial"
    })

    time.sleep(0.5)

    # Tutorial rápido
    mensaje_tutorial = f"{CELEBRACION} ¡Perfecto!\n\n"
    mensaje_tutorial += f"{IDEA} *Comandos útiles:*\n\n"
    mensaje_tutorial += f"1{NIVEL_UP} Escribe *'menu'* {MENU}\n"
    mensaje_tutorial += f"   Para ver todas las opciones\n\n"
    mensaje_tutorial += f"2{NIVEL_UP} Escribe *'ayuda'* {IDEA}\n"
    mensaje_tutorial += f"   Si necesitas una pista\n\n"
    mensaje_tutorial += f"3{NIVEL_UP} Escribe *'perfil'* {PERFIL}\n"
    mensaje_tutorial += f"   Para ver tu progreso\n\n"
    mensaje_tutorial += f"{PREGUNTA} ¿Listo para empezar?"

    botones = [
        {"id": "finalizar_onboarding", "title": f"¡Vamos! {COHETE}"}
    ]
    enviar_botones_basicos(numero_remitente, mensaje_tutorial, botones)


def finalizar_onboarding_y_empezar(numero_remitente, usuario):
    """
    Marca el onboarding como completado y otorga el primer logro.
    """
    # Marcar como completado
    db.actualizar_usuario(numero_remitente, {
        "onboarding_completado": 1,
        "estado_conversacion": "menu_principal"
    })

    # Desbloquear logro "Primer Paso"
    logros_actuales = json.loads(usuario.get("logros_desbloqueados", "[]"))
    if "primer_paso" not in logros_actuales:
        logros_actuales.append("primer_paso")
        db.actualizar_usuario(numero_remitente, {
            "logros_desbloqueados": json.dumps(logros_actuales)
        })

        # Mensaje de logro
        logro = LOGROS_DISPONIBLES["primer_paso"]
        mensaje_logro = formatear_logro_desbloqueado(
            logro["nombre"],
            logro["descripcion"],
            logro["emoji"]
        )
        responder_mensaje(numero_remitente, mensaje_logro, [])

        # Bonus de puntos
        puntos_actuales = usuario.get("puntos", 0)
        db.actualizar_usuario(numero_remitente, {
            "puntos": puntos_actuales + logro["puntos_bonus"]
        })

        time.sleep(1)

    # Mostrar menú principal
    preferencia = usuario.get("preferencia_aprendizaje", "ambos")

    if preferencia == "curso":
        mensaje = f"{COHETE} ¡Genial! Empecemos con tu primer tema de Java"
        responder_mensaje(numero_remitente, mensaje, [])
        time.sleep(1)
        enviar_menu_interactivo(numero_remitente)
    elif preferencia == "retos":
        mensaje = f"{COHETE} ¡Perfecto! Vamos a practicar con retos"
        responder_mensaje(numero_remitente, mensaje, [])
        time.sleep(1)
        enviar_menu_interactivo(numero_remitente)
    else:
        mensaje = f"{COHETE} ¡Excelente! Tienes todo a tu disposición"
        responder_mensaje(numero_remitente, mensaje, [])
        time.sleep(1)
        enviar_menu_interactivo(numero_remitente)