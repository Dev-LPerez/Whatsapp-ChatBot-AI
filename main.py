# main.py

import json
from fastapi import FastAPI, Request, Response
from datetime import date

import database as db
import message_handler as handler
from whatsapp_utils import enviar_botones_basicos

app = FastAPI()

@app.post("/webhook")
async def recibir_mensaje(request: Request):
    body = await request.json()
    print(json.dumps(body, indent=2))
    try:
        # Extrae la información relevante del payload de WhatsApp
        entry = body.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})
        
        if not value: return Response(status_code=200)

        # Si es un mensaje, procesarlo
        if 'messages' in value and value['messages']:
            message_data = value['messages'][0]
            numero_remitente = message_data['from']
            nombre_usuario = value['contacts'][0]['profile']['name']
            
            # --- Gestión del ciclo de vida del usuario ---
            usuario = db.obtener_usuario(numero_remitente)
            
            # RF-01: Registro de nuevo usuario
            if not usuario:
                db.crear_usuario(numero_remitente, nombre_usuario)
                bienvenida = f"¡Hola, {nombre_usuario}! 👋 Soy LogicBot, tu tutor de IA personal. ¡Estoy aquí para ayudarte a pensar como un programador! 🚀"
                botones_inicio = [{"id": "mostrar_menu", "title": "Ver Menú Principal"}]
                enviar_botones_basicos(numero_remitente, bienvenida, botones_inicio)
                return Response(status_code=200)

            # Actualización de la racha de días
            if usuario.get("ultima_conexion") != str(date.today()):
                ayer = date.fromisoformat(usuario.get("ultima_conexion", "1970-01-01"))
                racha = usuario.get("racha_dias", 0) if (date.today() - ayer).days == 1 else 0
                db.actualizar_usuario(numero_remitente, {"ultima_conexion": str(date.today()), "racha_dias": racha + 1})
            
            # --- Delegación al manejador de mensajes ---
            if message_data.get('type') == 'interactive':
                interactive_type = message_data['interactive']['type']
                id_seleccion = message_data['interactive'][interactive_type]['id']
                handler.handle_interactive_message(id_seleccion, numero_remitente, usuario)
            
            elif message_data.get('type') == 'text':
                mensaje_texto = message_data['text']['body']
                handler.handle_text_message(mensaje_texto, numero_remitente, usuario)

    except Exception as e:
        print(f"Ocurrió un error no manejado: {e}")
        # Considera registrar el error en un sistema de logging más robusto
    
    return Response(status_code=200)


@app.on_event("startup")
async def startup_event():
    db.inicializar_db()

@app.get("/webhook")
async def verificar_webhook(request: Request):
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "micodigosecreto") # Lee desde env
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode and token and mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, status_code=200)
    return Response(status_code=403)