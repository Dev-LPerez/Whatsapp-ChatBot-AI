# whatsapp_utils.py

import os
import json
import requests
from database import actualizar_usuario

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
ID_NUMERO_TELEFONO = os.getenv("ID_NUMERO_TELEFONO")

def responder_mensaje(numero_destinatario, texto_respuesta, historial_actual=[]):
    """Envía un mensaje de texto a través de la API de WhatsApp Cloud."""
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