# main.py (LogicBot v5.1 - Navegación por Botones)

import json
from fastapi import FastAPI, Request, Response
from datetime import date

import database as db
import ai_services as ai
from whatsapp_utils import responder_mensaje, enviar_menu_interactivo, enviar_botones_basicos

app = FastAPI()

CURSOS = {
    "python": {
        "nombre": "Python Essentials 🐍",
        "lecciones": ["Variables y Tipos de Datos", "Operadores Aritméticos", "Condicionales (if/else)", "Bucles (for y while)", "Funciones"]
    }
}
UMBRAL_DE_FALLOS = 2

def manejar_seleccion_menu(id_seleccion, numero_remitente, usuario):
    # ... (Esta función auxiliar no necesita cambios)
    pass # La lógica se movió abajo para mayor claridad

@app.post("/webhook")
async def recibir_mensaje(request: Request):
    body = await request.json()
    print(json.dumps(body, indent=2))
    try:
        value = body['entry'][0]['changes'][0]['value']
        if not (value.get("messages") and value['messages'][0]): return Response(status_code=200)
        
        message_data = value['messages'][0]
        numero_remitente = message_data['from']
        nombre_usuario = value['contacts'][0]['profile']['name']
        usuario = db.obtener_usuario(numero_remitente)
        
        if not usuario:
            db.crear_usuario(numero_remitente, nombre_usuario)
            bienvenida = (f"¡Hola, {nombre_usuario}! 👋 Soy LogicBot, tu tutor de IA personal. ¡Estoy aquí para ayudarte a pensar como un programador! 🚀")
            enviar_botones_basicos(numero_remitente, bienvenida)
            return Response(status_code=200)

        # (Lógica de racha sin cambios)
        if usuario.get("ultima_conexion") != str(date.today()):
            ayer = date.fromisoformat(usuario.get("ultima_conexion", "1970-01-01"))
            racha = usuario.get("racha_dias", 0) if (date.today() - ayer).days == 1 else 0
            db.actualizar_usuario(numero_remitente, {"ultima_conexion": str(date.today()), "racha_dias": racha + 1})
            usuario["racha_dias"] = racha + 1

        # --- DETECCIÓN DE TIPO DE MENSAJE (TEXTO O INTERACTIVO) ---
        if message_data.get('type') == 'interactive':
            interactive_type = message_data['interactive']['type']
            id_seleccion = message_data['interactive'][interactive_type]['id']
            
            # Si el usuario presiona un botón de respuesta rápida
            if id_seleccion == 'mostrar_menu':
                enviar_menu_interactivo(numero_remitente)
            
            # Si el usuario elige una opción del menú de lista
            else:
                historial_chat = json.loads(usuario.get("historial_chat", "[]"))
                if id_seleccion == "iniciar_curso_python":
                    curso = CURSOS["python"]
                    leccion_actual = 0
                    db.actualizar_usuario(numero_remitente, {"estado_conversacion": "en_curso", "curso_actual": "python", "leccion_actual": leccion_actual, "intentos_fallidos": 0})
                    mensaje_inicio = (f"¡Excelente! 🎉 Iniciaste el curso: *{curso['nombre']}*.\n\nTu primera lección: **{curso['lecciones'][leccion_actual]}**.\n\nGenerando tu primer reto...")
                    responder_mensaje(numero_remitente, mensaje_inicio, historial_chat)
                    tematica = curso['lecciones'][leccion_actual]
                    reto = ai.generar_reto_con_ia(usuario['nivel'], "Python", "Fácil", tematica)
                    if "error" in reto:
                        responder_mensaje(numero_remitente, reto["error"], historial_chat)
                    else:
                        db.actualizar_usuario(numero_remitente, {"reto_actual_enunciado": reto["enunciado"], "reto_actual_solucion": reto["solucion_ideal"], "reto_actual_pistas": json.dumps(reto["pistas"]), "pistas_usadas": 0, "reto_actual_tipo": "Python"})
                        responder_mensaje(numero_remitente, reto["enunciado"], historial_chat)
                elif id_seleccion == "pedir_reto_aleatorio":
                    db.actualizar_usuario(numero_remitente, {"curso_actual": None, "estado_conversacion": "eligiendo_dificultad", "tipo_reto_actual": "Python"})
                    responder_mensaje(numero_remitente, "¿Qué nivel de dificultad prefieres? 🤔\n\n1. Fácil 🌱\n2. Intermedio 🔥\n3. Difícil 🤯", historial_chat)
                elif id_seleccion == "ver_mi_perfil":
                    perfil = (f"📊 *Tu Perfil de LogicBot*\n\n👤 *Nombre:* {usuario['nombre']}\n🎓 *Nivel:* {usuario['nivel']}\n⭐ *Puntos:* {usuario.get('puntos', 0)}\n🔥 *Racha:* {usuario.get('racha_dias', 0)} día(s)")
                    responder_mensaje(numero_remitente, perfil, historial_chat)
            return Response(status_code=200)

        # --- LÓGICA PARA MENSAJES DE TEXTO ---
        mensaje_texto = message_data['text']['body']
        historial_chat = json.loads(usuario.get("historial_chat", "[]"))
        historial_chat.append({"usuario": mensaje_texto})
        estado = usuario.get("estado_conversacion", "menu_principal")
        mensaje_lower = mensaje_texto.lower()

        if mensaje_lower == "menu":
            enviar_menu_interactivo(numero_remitente)
        
        # ... (El resto del código para manejar estados como "eligiendo_dificultad", soluciones, pistas, etc., no cambia)
        else:
            # Fallback: si no se entiende el texto, ofrecer el menú con botones
            enviar_botones_basicos(numero_remitente, "No he entendido muy bien tu mensaje. ¿Qué te gustaría hacer?")

    except Exception as e:
        print(f"Ocurrió un error no manejado: {e}")
    return Response(status_code=200)

@app.on_event("startup")
async def startup_event():
    db.inicializar_db()

@app.get("/webhook")
async def verificar_webhook(request: Request):
    VERIFY_TOKEN = "micodigosecreto"
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode and token and mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, status_code=200)
    return Response(status_code=403)