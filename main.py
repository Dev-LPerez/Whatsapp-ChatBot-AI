# main.py

import json
import os
import time
from fastapi import FastAPI, Request, Response
from datetime import date, datetime

import database as db
import message_handler as handler
from whatsapp_utils import enviar_botones_basicos
# --- ✅ IMPORTACIÓN AGREGADA ---
from message_components import iniciar_onboarding

app = FastAPI(
    title="LogicBot API",
    description="Chatbot educativo de programación para WhatsApp",
    version="1.0.3"
)

# Variable global para rastrear el tiempo de inicio
app_start_time = time.time()


@app.on_event("startup")
async def startup_event():
    """
    Esta función se ejecuta una sola vez cuando la aplicación arranca.
    Llama a la inicialización inteligente de la base de datos.
    """
    print("=" * 60)
    print("🤖 LogicBot - Iniciando servidor...")
    print("=" * 60)
    print(f"⏰ Hora de inicio: {datetime.fromtimestamp(app_start_time).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Entorno: {'Producción (Render)' if os.getenv('RENDER') else 'Desarrollo Local'}")
    print(f"🔌 Puerto: {os.getenv('PORT', '8000')}")

    # Inicializar base de datos
    db.inicializar_db()

    print("✅ Servidor listo para recibir peticiones")
    print("=" * 60)


@app.post("/webhook")
async def recibir_mensaje(request: Request):
    body = await request.json()
    try:
        entry = body.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})

        if not value: return Response(status_code=200)

        if 'statuses' in value: return Response(status_code=200)
        if 'messages' not in value: return Response(status_code=200)

        if value['messages']:
            message_data = value['messages'][0]
            numero_remitente = str(message_data['from'])

            profile = value.get('contacts', [{}])[0].get('profile', {})
            nombre_usuario = profile.get('name', "Estudiante")

            print(f"📩 Mensaje recibido de: {nombre_usuario} ({numero_remitente})")

            usuario = db.obtener_usuario(numero_remitente)

            # RF-01: Registro de nuevo usuario
            if not usuario:
                print(f"👤 Usuario nuevo detectado: {numero_remitente}. Registrando...")
                db.crear_usuario(numero_remitente, nombre_usuario)
                # --- ✅ LLAMADA AHORA CORRECTA ---
                iniciar_onboarding(numero_remitente, nombre_usuario)
                return Response(status_code=200)

            # Actualización de racha
            if usuario.get("ultima_conexion") != str(date.today()):
                try:
                    ayer = date.fromisoformat(usuario.get("ultima_conexion", "1970-01-01"))
                    dias_diferencia = (date.today() - ayer).days
                    racha_actual = usuario.get("racha_dias", 0)
                    nueva_racha = racha_actual + 1 if dias_diferencia == 1 else 1
                    db.actualizar_usuario(numero_remitente,
                                          {"ultima_conexion": str(date.today()), "racha_dias": nueva_racha})
                except ValueError:
                    db.actualizar_usuario(numero_remitente, {"ultima_conexion": str(date.today())})

            # Delegación de mensajes
            if message_data.get('type') == 'interactive':
                interactive_type = message_data['interactive']['type']
                id_seleccion = message_data['interactive'][interactive_type]['id']
                handler.handle_interactive_message(id_seleccion, numero_remitente, usuario)

            elif message_data.get('type') == 'text':
                mensaje_texto = message_data['text']['body']
                handler.handle_text_message(mensaje_texto, numero_remitente, usuario)

    except Exception as e:
        print(f"❌ Error en webhook: {e}")

    return Response(status_code=200)


@app.get("/")
async def root():
    return {"status": "🟢 online", "service": "LogicBot API", "version": "1.0.3"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/webhook")
async def verificar_webhook(request: Request):
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "micodigosecreto")
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token and mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, status_code=200)
    return Response(status_code=403)