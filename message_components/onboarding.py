# message_components/onboarding.py
        enviar_menu_interactivo(numero_remitente)
        time.sleep(1)
        responder_mensaje(numero_remitente, mensaje, [])
        mensaje = f"{COHETE} ¡Excelente! Tienes todo a tu disposición"
    else:
        enviar_menu_interactivo(numero_remitente)
        time.sleep(1)
        responder_mensaje(numero_remitente, mensaje, [])
        mensaje = f"{COHETE} ¡Perfecto! Vamos a practicar con retos"
    elif preferencia == "retos":
        enviar_menu_interactivo(numero_remitente)
        time.sleep(1)
        responder_mensaje(numero_remitente, mensaje, [])
        mensaje = f"{COHETE} ¡Genial! Empecemos con tu primer tema de Java"
    if preferencia == "curso":

    preferencia = usuario.get("preferencia_aprendizaje", "ambos")
    # Mostrar menú principal

        time.sleep(1)

        })
            "puntos": puntos_actuales + logro["puntos_bonus"]
        db.actualizar_usuario(numero_remitente, {
        puntos_actuales = usuario.get("puntos", 0)
        # Bonus de puntos

        responder_mensaje(numero_remitente, mensaje_logro, [])
        )
            logro["emoji"]
            logro["descripcion"],
            logro["nombre"],
        mensaje_logro = formatear_logro_desbloqueado(
        logro = LOGROS_DISPONIBLES["primer_paso"]
        # Mensaje de logro

        })
            "logros_desbloqueados": json.dumps(logros_actuales)
        db.actualizar_usuario(numero_remitente, {
        logros_actuales.append("primer_paso")
    if "primer_paso" not in logros_actuales:
    logros_actuales = json.loads(usuario.get("logros_desbloqueados", "[]"))
    # Desbloquear logro "Primer Paso"

    })
        "estado_conversacion": "menu_principal"
        "onboarding_completado": 1,
    db.actualizar_usuario(numero_remitente, {
    # Marcar como completado
    """
    Marca el onboarding como completado y otorga el primer logro.
    """
def finalizar_onboarding_y_empezar(numero_remitente, usuario):


    enviar_botones_basicos(numero_remitente, mensaje_tutorial, botones)
    ]
        {"id": "finalizar_onboarding", "title": f"¡Vamos! {COHETE}"}
    botones = [

    mensaje_tutorial += f"{PREGUNTA} ¿Listo para empezar?"
    mensaje_tutorial += f"   Para ver tu progreso\n\n"
    mensaje_tutorial += f"3{NIVEL_UP} Escribe *'perfil'* {PERFIL}\n"
    mensaje_tutorial += f"   Si necesitas una pista\n\n"
    mensaje_tutorial += f"2{NIVEL_UP} Escribe *'ayuda'* {IDEA}\n"
    mensaje_tutorial += f"   Para ver todas las opciones\n\n"
    mensaje_tutorial += f"1{NIVEL_UP} Escribe *'menu'* {MENU}\n"
    mensaje_tutorial += f"{IDEA} *Comandos útiles:*\n\n"
    mensaje_tutorial = f"{CELEBRACION} ¡Perfecto!\n\n"
    # Tutorial rápido

    time.sleep(0.5)

    })
        "estado_conversacion": "onboarding_tutorial"
        "preferencia_aprendizaje": preferencia,
    db.actualizar_usuario(numero_remitente, {
    # Guardar preferencia
    """
    Completa el onboarding y muestra el tutorial rápido.
    """
def completar_onboarding(numero_remitente, preferencia):


    enviar_botones_basicos(numero_remitente, mensaje, botones)
    ]
        {"id": "pref_ambos", "title": f"Ambas cosas {ESTRELLA}"}
        {"id": "pref_retos", "title": f"Practicar con retos {PRACTICA}"},
        {"id": "pref_curso", "title": f"Aprender desde cero {LIBRO}"},
    botones = [
    mensaje = f"{PREGUNTA} ¿Qué prefieres hacer?"

    })
        "estado_conversacion": "onboarding_paso_2"
        "nivel_inicial": nivel_seleccionado,
    db.actualizar_usuario(numero_remitente, {
    # Guardar nivel inicial
    """
    Pregunta 2: Preferencia de aprendizaje.
    """
def handle_onboarding_paso_2(numero_remitente, nivel_seleccionado):


    enviar_botones_basicos(numero_remitente, mensaje, botones)
    ]
        {"id": "nivel_avanzado", "title": f"Bastante {COHETE}"}
        {"id": "nivel_intermedio", "title": f"Un poco {INTERMEDIO}"},
        {"id": "nivel_principiante", "title": f"Nunca {FACIL}"},
    botones = [
    mensaje = f"{PREGUNTA} ¿Has programado en Java antes?"
    """
    Pregunta 1: Nivel de experiencia.
    """
def handle_onboarding_paso_1(numero_remitente):


    db.actualizar_usuario(numero_remitente, {"estado_conversacion": "onboarding_paso_1"})
    # Actualizar estado

    enviar_botones_basicos(numero_remitente, mensaje_propuesta, botones)
    botones = [{"id": "onboarding_empezar", "title": f"Empezar {COHETE}"}]
    mensaje_propuesta = f"{PREGUNTA} Antes de empezar...\n\nVoy a hacerte 2 preguntas rápidas para personalizar tu experiencia {ESTRELLA}"
    # Mensaje 2: Propuesta

    time.sleep(1)

    responder_mensaje(numero_remitente, mensaje_bienvenida, [])
    mensaje_bienvenida = f"¡Hola {nombre_usuario}! {ROBOT}\n\nSoy LogicBot {CODIGO}\nTu tutor personal de Java"
    # Mensaje 1: Bienvenida personalizada
    """
    Inicia el flujo de onboarding para nuevos usuarios.
    """
def iniciar_onboarding(numero_remitente, nombre_usuario):

import time
import json
from config import LOGROS_DISPONIBLES
from utils.formatters import formatear_logro_desbloqueado
from utils.emojis import *
from whatsapp_utils import enviar_botones_basicos, responder_mensaje, enviar_menu_interactivo
import database as db

# Sistema de onboarding personalizado

