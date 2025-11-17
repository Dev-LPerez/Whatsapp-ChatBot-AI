# main.py

import json
import os
import time
from fastapi import FastAPI, Request, Response
from datetime import date, datetime

import database as db
import message_handler as handler
from whatsapp_utils import enviar_botones_basicos

app = FastAPI(
    title="LogicBot API",
    description="Chatbot educativo de programación para WhatsApp",
    version="1.0.0"
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
    print(json.dumps(body, indent=2))
    try:
        # Extrae la información relevante del payload de WhatsApp
        entry = body.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})

        if not value:
            return Response(status_code=200)

        # IMPORTANTE: Filtrar webhooks de estado (entrega, lectura, etc.)
        # WhatsApp envía webhooks para: mensajes, estados, errores, etc.
        # Solo queremos procesar MENSAJES del usuario

        # Si contiene 'statuses', es un webhook de estado → IGNORAR
        if 'statuses' in value:
            print("⏭️  Webhook de estado ignorado (sent/delivered/read)")
            return Response(status_code=200)

        # Si NO contiene 'messages', no es un mensaje del usuario → IGNORAR
        if 'messages' not in value:
            print("⏭️  Webhook sin mensajes ignorado")
            return Response(status_code=200)

        # Si llegamos aquí, es un mensaje real del usuario
        if value['messages']:
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

    return Response(status_code=200)


@app.get("/")
async def root():
    """
    Endpoint raíz - Health check básico.
    Útil para verificar que el servicio está activo.
    """
    return {
        "status": "🟢 online",
        "service": "LogicBot API",
        "version": "1.0.0",
        "message": "El bot está funcionando correctamente"
    }

@app.get("/health")
async def health_check():
    """
    Endpoint de health check completo.
    Render y servicios de monitoreo pueden usar esto para verificar el estado.
    """
    # Calcular uptime en segundos
    uptime_seconds = int(time.time() - app_start_time)
    uptime_formatted = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s"

    # Verificar conexión a la base de datos
    db_status = "🟢 conectada"
    try:
        # Intento rápido de consulta
        test_user = db.obtener_usuario("health_check_test")
        db_status = "🟢 conectada"
    except Exception as e:
        db_status = f"🔴 error: {str(e)[:50]}"

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": uptime_seconds,
        "uptime": uptime_formatted,
        "environment": "production" if os.getenv('RENDER') else "development",
        "database": db_status,
        "services": {
            "whatsapp_api": "🟢 configurada" if os.getenv('WHATSAPP_TOKEN') else "🔴 no configurada",
            "gemini_ai": "🟢 configurada" if os.getenv('GEMINI_API_KEY') else "🔴 no configurada"
        }
    }

@app.get("/webhook")
async def verificar_webhook(request: Request):
    """
    Verificación de webhook de WhatsApp.
    Meta lo llama al configurar el webhook por primera vez.
    """
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "micodigosecreto")
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token and mode == "subscribe" and token == VERIFY_TOKEN:
        print(f"✅ Webhook verificado correctamente")
        return Response(content=challenge, status_code=200)

    print(f"❌ Verificación de webhook fallida")
    return Response(status_code=403)

