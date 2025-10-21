# whatsapp_utils.py

import os
import json
import requests
from database import actualizar_usuario
from config import CURSOS # <--- IMPORTANTE: Añadir esta línea

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
ID_NUMERO_TELEFONO = os.getenv("ID_NUMERO_TELEFONO")

def responder_mensaje(numero_destinatario, texto_respuesta, historial_actual=[]):
    if not WHATSAPP_TOKEN or not ID_NUMERO_TELEFONO: return
    
    nuevo_historial = historial_actual + [{"bot": texto_respuesta}]
    actualizar_usuario(numero_destinatario, {"historial_chat": json.dumps(nuevo_historial[-6:])})
    
    url = f"https://graph.facebook.com/v19.0/{ID_NUMERO_TELEFONO}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": numero_destinatario, "text": {"preview_url": False, "body": texto_respuesta}}
    
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
            "header": {"type": "text", "text": "LogicBot - Tutor de Java"},
            "body": {"text": "¡Hola! 👋 Elige una opción para comenzar a aprender y practicar Java."},
            "footer": {"text": "Tu progreso se guarda automáticamente"},
            "action": {
                "button": "Ver Opciones",
                "sections": [
                    {
                        "title": "🚀 Ruta de Aprendizaje", 
                        "rows": [
                            # Este ID ahora abrirá el menú de temas
                            {"id": "mostrar_temas_java", "title": "☕ Empezar Curso de Java"}
                        ]
                    },
                    {
                        "title": "💪 Práctica Libre",
                        "rows": [
                            {"id": "pedir_reto_aleatorio", "title": "🎲 Pedir Reto de Java"}
                        ]
                    },
                    {
                        "title": "📊 Mi Progreso",
                        "rows": [
                            {"id": "ver_mi_perfil", "title": "👤 Ver Mi Perfil"}
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

# --- ✅ NUEVA FUNCIÓN AÑADIDA ---
def enviar_menu_temas_java(numero_destinatario):
    """Envía un menú interactivo con los temas del curso de Java."""
    if not WHATSAPP_TOKEN or not ID_NUMERO_TELEFONO: return
    
    url = f"https://graph.facebook.com/v19.0/{ID_NUMERO_TELEFONO}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    
    # Creamos las filas (botones) dinámicamente desde config.py
    filas_temas = []
    for i, leccion in enumerate(CURSOS["java"]["lecciones"]):
        filas_temas.append({
            "id": f"iniciar_leccion_{i}", # ID único para cada lección
            "title": leccion
        })

    data = {
        "messaging_product": "whatsapp",
        "to": numero_destinatario,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": "Temas de Java"},
            "body": {"text": "¡Excelente! Elige el tema que te gustaría practicar hoy. 🧠"},
            "footer": {"text": "Selecciona un tema para empezar"},
            "action": {
                "button": "Ver Temas",
                "sections": [
                    {
                        "title": "Fundamentos de Java",
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


def enviar_botones_basicos(numero_destinatario, texto_principal, botones):
    """Envía un mensaje con hasta 3 botones de respuesta rápida."""
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
        if response.text:
            print(f"Respuesta de la API: {response.text}")