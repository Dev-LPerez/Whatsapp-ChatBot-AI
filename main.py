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
    version="1.0.1"
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
    # print(json.dumps(body, indent=2)) # Descomentar si necesitas ver todo el JSON crudo
    try:
        # Extrae la información relevante del payload de WhatsApp
        entry = body.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})

        if not value:
            return Response(status_code=200)

        # IMPORTANTE: Filtrar webhooks de estado (entrega, lectura, etc.)
        # WhatsApp envía eventos cuando un mensaje se envía, entrega o lee.
        # No queremos procesar esos eventos, solo mensajes nuevos.
        if 'statuses' in value:
            # print("⏭️  Webhook de estado ignorado (sent/delivered/read)")
            return Response(status_code=200)

        # Si NO contiene 'messages', no es un mensaje del usuario → IGNORAR
        if 'messages' not in value:
            return Response(status_code=200)

        # Si llegamos aquí, es un mensaje real del usuario
        if value['messages']:
            message_data = value['messages'][0]

            # --- 🛠️ CORRECCIÓN CRÍTICA APLICADA AQUÍ ---
            # Convertimos explícitamente el número a string (texto).
            # Esto asegura que coincida con el tipo de dato en la base de datos
            # y evita que el bot "olvide" al usuario, solucionando el bucle.
            numero_remitente = str(message_data['from'])

            # Intentamos obtener el nombre, si no existe usamos "Estudiante"
            profile = value.get('contacts', [{}])[0].get('profile', {})
            nombre_usuario = profile.get('name', "Estudiante")

            print(f"📩 Mensaje recibido de: {nombre_usuario} ({numero_remitente})")

            # --- Gestión del ciclo de vida del usuario ---
            usuario = db.obtener_usuario(numero_remitente)

            # RF-01: Registro de nuevo usuario
            if not usuario:
                print(f"👤 Usuario nuevo (o no encontrado) detectado: {numero_remitente}. Registrando...")
                db.crear_usuario(numero_remitente, nombre_usuario)

                # Mensaje de bienvenida solo para usuarios nuevos
                bienvenida = f"¡Hola, {nombre_usuario}! 👋 Soy LogicBot, tu tutor de IA personal. ¡Estoy aquí para ayudarte a pensar como un programador! 🚀"
                botones_inicio = [{"id": "mostrar_menu", "title": "Ver Menú Principal"}]
                enviar_botones_basicos(numero_remitente, bienvenida, botones_inicio)
                return Response(status_code=200)

            # Actualización de la racha de días (si ya existe el usuario)
            if usuario.get("ultima_conexion") != str(date.today()):
                try:
                    ayer = date.fromisoformat(usuario.get("ultima_conexion", "1970-01-01"))
                    # Si se conectó ayer, incrementamos racha, si no, reiniciamos a 1
                    dias_diferencia = (date.today() - ayer).days
                    racha_actual = usuario.get("racha_dias", 0)

                    nueva_racha = racha_actual + 1 if dias_diferencia == 1 else 1

                    db.actualizar_usuario(numero_remitente, {
                        "ultima_conexion": str(date.today()),
                        "racha_dias": nueva_racha
                    })
                except ValueError:
                    # Si hay error con la fecha, simplemente actualizamos al día de hoy
                    db.actualizar_usuario(numero_remitente, {"ultima_conexion": str(date.today())})

            # --- Delegación al manejador de mensajes ---
            if message_data.get('type') == 'interactive':
                interactive_type = message_data['interactive']['type']
                id_seleccion = message_data['interactive'][interactive_type]['id']
                handler.handle_interactive_message(id_seleccion, numero_remitente, usuario)

            elif message_data.get('type') == 'text':
                mensaje_texto = message_data['text']['body']
                handler.handle_text_message(mensaje_texto, numero_remitente, usuario)

    except Exception as e:
        print(f"❌ Ocurrió un error no manejado en el webhook: {e}")

    return Response(status_code=200)


@app.get("/")
async def root():
    """
    Endpoint raíz - Health check básico.
    """
    return {
        "status": "🟢 online",
        "service": "LogicBot API",
        "version": "1.0.2 (Fix Bucle Bienvenida)",
        "message": "El bot está funcionando correctamente"
    }


@app.get("/health")
async def health_check():
    """
    Endpoint de health check completo.
    """
    uptime_seconds = int(time.time() - app_start_time)
    uptime_formatted = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s"

    db_status = "🟢 conectada"
    try:
        # Intento rápido de consulta para verificar DB
        _ = db.obtener_usuario("health_check_test")
        db_status = "🟢 conectada"
    except Exception as e:
        db_status = f"🔴 error: {str(e)[:50]}"

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": uptime_formatted,
        "environment": "production" if os.getenv('RENDER') else "development",
        "database": db_status
    }


@app.get("/webhook")
async def verificar_webhook(request: Request):
    """
    Verificación de webhook de WhatsApp.
    """
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "micodigosecreto")
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token and mode == "subscribe" and token == VERIFY_TOKEN:
        print(f"✅ Webhook verificado correctamente")
        return Response(content=challenge, status_code=200)

    print(f"❌ Verificación de webhook fallida. Token recibido: {token}")
    return Response(status_code=403)