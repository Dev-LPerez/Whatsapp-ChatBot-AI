# whatsapp_utils.py

import os
import json
import requests
from database import actualizar_usuario

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
ID_NUMERO_TELEFONO = os.getenv("ID_NUMERO_TELEFONO")

def responder_mensaje(numero_destinatario, texto_respuesta, historial_actual=[]):
    if not WHATSAPP_TOKEN or not ID_NUMERO_TELEFONO: return
    nuevo_historial = historial_actual + [{"bot": texto_respuesta}]
    actualizar_usuario(numero_destinatario, {"historial_chat": json.dumps(nuevo_historial[-4:])})
    url = f"https://graph.facebook.com/v19.0/{ID_NUMERO_TELEFONO}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": numero_destinatario, "text": {"preview_url": False, "body": texto_respuesta}}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar mensaje a {numero_destinatario}: {e}")

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
            "body": {
                "text": "¡Hola! Soy tu tutor de IA. Elige una de las siguientes opciones para comenzar."
            },
            "action": {
                "button": "Ver Opciones",
                "sections": [
                    {
                        "title": "Aprender y Practicar",
                        "rows": [
                            {"id": "iniciar_curso_python", "title": "🐍 Empezar Curso"},
                            {"id": "pedir_reto_aleatorio", "title": "💪 Reto Aleatorio"}
                        ]
                    },
                    {
                        "title": "Mi Progreso",
                        "rows": [
                            {"id": "ver_mi_perfil", "title": "📊 Ver Mi Perfil"}
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

def enviar_botones_basicos(numero_destinatario, texto_principal):
    """Envía un mensaje con hasta 3 botones de respuesta rápida."""
    if not WHATSAPP_TOKEN or not ID_NUMERO_TELEFONO: return
    url = f"https://graph.facebook.com/v19.0/{ID_NUMERO_TELEFONO}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": numero_destinatario,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": texto_principal
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "mostrar_menu",
                            "title": "Ver Menú Principal"
                        }
                    }
                ]
            }
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar botones a {numero_destinatario}: {e}")