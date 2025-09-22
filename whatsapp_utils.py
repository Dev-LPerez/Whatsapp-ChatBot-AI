# whatsapp_utils.py

import os
import json
import requests
from database import actualizar_usuario

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
ID_NUMERO_TELEFONO = os.getenv("ID_NUMERO_TELEFONO")

def responder_mensaje(numero_destinatario, texto_respuesta, historial_actual=[]):
    """Envía un mensaje de texto simple a través de la API de WhatsApp Cloud."""
    if not WHATSAPP_TOKEN or not ID_NUMERO_TELEFONO:
        print("Error: Variables de entorno de WhatsApp no configuradas.")
        return

    nuevo_historial = historial_actual + [{"bot": texto_respuesta}]
    actualizar_usuario(numero_destinatario, {"historial_chat": json.dumps(nuevo_historial[-4:])})

    url = f"https://graph.facebook.com/v19.0/{ID_NUMERO_TELEFONO}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": numero_destinatario,
        "text": {"preview_url": False, "body": texto_respuesta}
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar mensaje a {numero_destinatario}: {e}")

def enviar_menu_interactivo(numero_destinatario):
    """Envía un menú de lista interactivo."""
    if not WHATSAPP_TOKEN or not ID_NUMERO_TELEFONO:
        print("Error: Variables de entorno de WhatsApp no configuradas.")
        return
        
    url = f"https://graph.facebook.com/v19.0/{ID_NUMERO_TELEFONO}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": numero_destinatario,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "🤖 LogicBot Tutor"
            },
            "body": {
                "text": "¡Hola! Soy tu tutor de IA. Elige una opción para comenzar a aprender y practicar."
            },
            "footer": {
                "text": "Selecciona una opción de la lista"
            },
            "action": {
                "button": "Ver Opciones",
                "sections": [
                    {
                        "title": "Aprender y Practicar",
                        "rows": [
                            {
                                "id": "iniciar_curso_python",
                                "title": "🐍 Empezar Curso de Python",
                                "description": "Aprende Python desde cero con una ruta guiada."
                            },
                            {
                                "id": "pedir_reto_aleatorio",
                                "title": "💪 Pedir Reto Aleatorio",
                                "description": "Pon a prueba tus habilidades con un reto al azar."
                            }
                        ]
                    },
                    {
                        "title": "Mi Progreso",
                        "rows": [
                            {
                                "id": "ver_mi_perfil",
                                "title": "📊 Ver Mi Perfil",
                                "description": "Consulta tus estadísticas, puntos y nivel."
                            }
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