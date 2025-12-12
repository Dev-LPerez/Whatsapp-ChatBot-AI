# whatsapp_utils.py

import os
import json
import requests
from src.database import actualizar_usuario
from src.config.config import CURSOS

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
ID_NUMERO_TELEFONO = os.getenv("ID_NUMERO_TELEFONO")


def responder_mensaje(numero_destinatario, texto_respuesta, historial_actual=[]):
    if not WHATSAPP_TOKEN or not ID_NUMERO_TELEFONO: return

    nuevo_historial = historial_actual + [{"bot": texto_respuesta}]
    actualizar_usuario(numero_destinatario, {"historial_chat": json.dumps(nuevo_historial[-6:])})

    url = f"https://graph.facebook.com/v19.0/{ID_NUMERO_TELEFONO}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": numero_destinatario,
            "text": {"preview_url": False, "body": texto_respuesta}}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar mensaje a {numero_destinatario}: {e}")
        if response.text:
            print(f"Respuesta de la API: {response.text}")


def enviar_menu_interactivo(numero_destinatario):
    if not WHATSAPP_TOKEN or not ID_NUMERO_TELEFONO: return
    url = f"https://graph.facebook.com/v19.0/{ID_NUMERO_TELEFONO}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": numero_destinatario,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": "LogicBot - Tu Tutor IA"},
            "body": {"text": "¡Hola! 👋 Aquí tienes tu centro de control."},
            "footer": {"text": "Selecciona una opción 👇"},
            "action": {
                "button": "Abrir Menú",
                "sections": [
                    {
                        "title": "🚀 Aprender",
                        "rows": [
                            {"id": "mostrar_temas_java", "title": "☕ Curso de Java",
                             "description": "Lecciones paso a paso"},
                            {"id": "pedir_reto_aleatorio", "title": "🎲 Reto Rápido",
                             "description": "Practicar algo al azar"}
                        ]
                    },
                    {
                        "title": "🎒 Mi Mochila",
                        "rows": [
                            {"id": "ver_coleccion", "title": "📚 Mis Fichas",
                             "description": "Cheat sheets desbloqueadas"},
                            {"id": "ver_logros", "title": "🏆 Mis Logros", "description": "Medallas ganadas"},
                            {"id": "ver_mi_perfil", "title": "👤 Mi Perfil", "description": "Nivel y estadísticas"}
                        ]
                    }
                ]
            }
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar menú a {numero_destinatario}: {e}")
        if response.text:
            print(f"Respuesta de la API: {response.text}")


def enviar_menu_temas_java(numero_destinatario):
    """Envía un menú interactivo con los temas del curso de Java."""
    if not WHATSAPP_TOKEN or not ID_NUMERO_TELEFONO: return

    url = f"https://graph.facebook.com/v19.0/{ID_NUMERO_TELEFONO}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}

    filas_temas = []
    for i, leccion in enumerate(CURSOS["java"]["lecciones"]):
        filas_temas.append({
            "id": f"iniciar_leccion_{i}",
            "title": leccion
        })

    data = {
        "messaging_product": "whatsapp",
        "to": numero_destinatario,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": "Temas de Java"},
            "body": {"text": "Selecciona un tema para comenzar la lección y el reto."},
            "footer": {"text": "👇 Elige tu camino"},
            "action": {
                "button": "Ver Temas",
                "sections": [
                    {
                        "title": "Fundamentos",
                        "rows": filas_temas
                    }
                ]
            }
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar menú de temas a {numero_destinatario}: {e}")
        if response.text:
            print(f"Respuesta de la API: {response.text}")


# --- ✅ NUEVA FUNCIÓN PARA MOSTRAR FICHAS DESBLOQUEADAS ---
def enviar_lista_recursos(numero_destinatario, recursos_desbloqueados):
    """Envía un menú lista con las fichas que el usuario ya desbloqueó."""
    if not WHATSAPP_TOKEN or not ID_NUMERO_TELEFONO: return

    url = f"https://graph.facebook.com/v19.0/{ID_NUMERO_TELEFONO}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}

    filas_recursos = []
    # recursos_desbloqueados es una lista de tuplas (indice, nombre_tema)
    for idx, tema in recursos_desbloqueados:
        filas_recursos.append({
            "id": f"ver_ficha_{idx}",
            "title": tema[:24],  # WhatsApp limita el título a 24 chars
            "description": "Ver Cheat Sheet"
        })

    data = {
        "messaging_product": "whatsapp",
        "to": numero_destinatario,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": "🎒 Tu Mochila"},
            "body": {"text": "Aquí están las fichas técnicas que has desbloqueado. Selecciónala para consultarla."},
            "footer": {"text": "¡Úsalas sabiamente!"},
            "action": {
                "button": "Ver Fichas",
                "sections": [
                    {
                        "title": "Recursos Disponibles",
                        "rows": filas_recursos
                    }
                ]
            }
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar lista de recursos: {e}")


def enviar_botones_basicos(numero_destinatario, texto_principal, botones):
    if not WHATSAPP_TOKEN or not ID_NUMERO_TELEFONO: return
    url = f"https://graph.facebook.com/v19.0/{ID_NUMERO_TELEFONO}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}

    action_buttons = []
    for boton in botones:
        action_buttons.append({
            "type": "reply",
            "reply": {
                "id": boton["id"],
                "title": boton["title"]
            }
        })

    data = {
        "messaging_product": "whatsapp",
        "to": numero_destinatario,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": texto_principal},
            "action": {"buttons": action_buttons}
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar botones a {numero_destinatario}: {e}")