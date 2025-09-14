# main.py (LogicBot v3.1 - Versión Refactorizada)

import json
from fastapi import FastAPI, Request, Response
from datetime import date

# Importaciones de los nuevos módulos
import database as db
import ai_services as ai
from whatsapp_utils import responder_mensaje

app = FastAPI()

# --- WEBHOOK (LÓGICA PRINCIPAL) ---
@app.post("/webhook")
async def recibir_mensaje(request: Request):
    body = await request.json()
    print(json.dumps(body, indent=2))
    try:
        value = body['entry'][0]['changes'][0]['value']
        if not (value.get("messages") and value['messages'][0]):
            return Response(status_code=200)
        
        numero_remitente = value['messages'][0]['from']
        mensaje_texto = value['messages'][0]['text']['body']
        nombre_usuario = value['contacts'][0]['profile']['name']

        usuario = db.obtener_usuario(numero_remitente)
        hoy_str = str(date.today())

        if not usuario:
            db.crear_usuario(numero_remitente, nombre_usuario)
            usuario = db.obtener_usuario(numero_remitente)
            bienvenida = (
                f"¡Hola, {nombre_usuario}! 👋 Soy LogicBot, tu tutor de IA personal.\n\n"
                "¡Estoy aquí para ayudarte a pensar como un programador! 🚀\n\n"
                "**Comandos disponibles:**\n"
                "- `reto python` (o java/pseudocodigo)\n"
                "- `mi perfil` para ver tus estadísticas."
            )
            responder_mensaje(numero_remitente, bienvenida, [])
            return Response(status_code=200)
        
        if usuario.get("ultima_conexion") != hoy_str:
            ayer = date.fromisoformat(usuario.get("ultima_conexion", "1970-01-01"))
            racha = usuario.get("racha_dias", 0) if (date.today() - ayer).days == 1 else 0
            db.actualizar_usuario(numero_remitente, {"ultima_conexion": hoy_str, "racha_dias": racha + 1})
            usuario["racha_dias"] = racha + 1

        historial_chat = json.loads(usuario.get("historial_chat", "[]"))
        historial_chat.append({"usuario": mensaje_texto})
        estado = usuario.get("estado_conversacion", "menu_principal")
        mensaje_lower = mensaje_texto.lower()

        # --- LÓGICA DE MANEJO DE COMANDOS ---
        if mensaje_lower.startswith("reto"):
            tipo_reto, tematica = None, None
            if "python" in mensaje_lower: tipo_reto = "Python"
            elif "java" in mensaje_lower: tipo_reto = "Java"
            elif "pseudo" in mensaje_lower: tipo_reto = "Pseudocódigo"
            if "sobre" in mensaje_lower: tematica = mensaje_texto.split("sobre", 1)[1].strip()
            
            if tipo_reto:
                db.actualizar_usuario(numero_remitente, {"estado_conversacion": "eligiendo_dificultad", "tipo_reto_actual": tipo_reto, "tematica_actual": tematica})
                responder_mensaje(numero_remitente, "¿Qué nivel de dificultad prefieres? 🤔\n\n1. Fácil 🌱\n2. Intermedio 🔥\n3. Difícil 🤯", historial_chat)
            else:
                responder_mensaje(numero_remitente, "Debes especificar un lenguaje. Ejemplo: `reto python sobre bucles`.", historial_chat)

        elif estado == "eligiendo_dificultad":
            dificultad = None
            if "1" in mensaje_texto or "fácil" in mensaje_lower: dificultad = "Fácil"
            elif "2" in mensaje_texto or "intermedio" in mensaje_lower: dificultad = "Intermedio"
            elif "3" in mensaje_texto or "difícil" in mensaje_lower: dificultad = "Difícil"
            
            if dificultad:
                tipo_reto = usuario["tipo_reto_actual"]
                tematica = usuario.get("tematica_actual")
                responder_mensaje(numero_remitente, f"¡Entendido! 👨‍💻 Buscando un reto de *{tipo_reto}* con dificultad *{dificultad}*...", historial_chat)
                reto = ai.generar_reto_con_ia(usuario['nivel'], tipo_reto, dificultad, tematica)
                if "error" in reto:
                    responder_mensaje(numero_remitente, reto["error"], historial_chat)
                    db.actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal"})
                else:
                    db.actualizar_usuario(numero_remitente, {"estado_conversacion": "resolviendo_reto", "reto_actual_enunciado": reto["enunciado"], "reto_actual_solucion": reto["solucion_ideal"], "reto_actual_pistas": json.dumps(reto["pistas"]), "pistas_usadas": 0})
                    responder_mensaje(numero_remitente, reto["enunciado"], historial_chat)
            else:
                responder_mensaje(numero_remitente, "Por favor, elige una dificultad: 1, 2 o 3.", historial_chat)

        elif mensaje_lower.startswith("solucion:"):
            if not usuario.get("reto_actual_enunciado"):
                responder_mensaje(numero_remitente, "¡Ups! 😅 No tienes un reto activo.", historial_chat)
            else:
                solucion_usuario = mensaje_texto[len("solucion:"):].strip()
                feedback = ai.evaluar_solucion_con_ia(usuario["reto_actual_enunciado"], solucion_usuario, usuario["reto_actual_tipo"])
                responder_mensaje(numero_remitente, feedback, historial_chat)
                if feedback.strip().upper().startswith("✅"):
                    puntos_ganados = 10 * usuario["racha_dias"]
                    puntos_totales = usuario.get("puntos", 0) + puntos_ganados
                    nivel_actual = usuario["nivel"]
                    nuevo_nivel = (puntos_totales // 100) + 1
                    db.actualizar_usuario(numero_remitente, {"puntos": puntos_totales, "nivel": nuevo_nivel, "estado_conversacion": "menu_principal", "reto_actual_enunciado": None})
                    mensaje_felicitacion = f"¡Ganaste *{puntos_ganados} puntos* (x{usuario['racha_dias']} de racha 🔥)! Tienes un total de {puntos_totales} puntos."
                    if nuevo_nivel > nivel_actual:
                        mensaje_felicitacion += f"\n\n🚀 ¡FELICIDADES! ¡Has subido al Nivel {nuevo_nivel}!"
                    responder_mensaje(numero_remitente, mensaje_felicitacion, historial_chat)
        
        elif mensaje_lower == "pista":
            if not usuario.get("reto_actual_enunciado"):
                responder_mensaje(numero_remitente, "No tienes un reto activo para pedir una pista.", historial_chat)
            else:
                pistas = json.loads(usuario.get("reto_actual_pistas", "[]"))
                pistas_usadas = usuario.get("pistas_usadas", 0)
                if pistas_usadas < len(pistas):
                    responder_mensaje(numero_remitente, f"🔍 *Pista {pistas_usadas + 1}/{len(pistas)}:* {pistas[pistas_usadas]}", historial_chat)
                    db.actualizar_usuario(numero_remitente, {"pistas_usadas": pistas_usadas + 1})
                else:
                    responder_mensaje(numero_remitente, "¡Ya has usado todas las pistas! 😥 Si quieres, puedes rendirte escribiendo `me rindo`.", historial_chat)
        
        elif mensaje_lower == "me rindo":
             if not usuario.get("reto_actual_solucion"):
                responder_mensaje(numero_remitente, "Tranquilo, no tienes ningún reto activo para rendirte. ¡Pide uno cuando quieras! 👍", historial_chat)
             else:
                respuesta_con_explicacion = ai.chat_conversacional_con_ia(mensaje_texto, historial_chat, usuario.get("reto_actual_solucion"))
                db.actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal", "reto_actual_enunciado": None})
                responder_mensaje(numero_remitente, respuesta_con_explicacion, historial_chat)

        elif mensaje_lower == "mi perfil":
            perfil = (
                f"📊 *Tu Perfil de LogicBot*\n\n"
                f"👤 *Nombre:* {usuario['nombre']}\n"
                f"🎓 *Nivel:* {usuario['nivel']}\n"
                f"⭐ *Puntos:* {usuario.get('puntos', 0)}\n"
                f"🔥 *Racha:* {usuario.get('racha_dias', 0)} día(s)"
            )
            responder_mensaje(numero_remitente, perfil, historial_chat)

        else:
            respuesta_chat = ai.chat_conversacional_con_ia(mensaje_texto, historial_chat, usuario.get("reto_actual_solucion"))
            responder_mensaje(numero_remitente, respuesta_chat, historial_chat)

    except Exception as e:
        print(f"Ocurrió un error no manejado: {e}")
    return Response(status_code=200)

@app.on_event("startup")
async def startup_event():
    """Inicializa la base de datos al iniciar la aplicación."""
    db.inicializar_db()

@app.get("/webhook")
async def verificar_webhook(request: Request):
    """Verifica el token de la API de WhatsApp."""
    VERIFY_TOKEN = "micodigosecreto"
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode and token and mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, status_code=200)
    return Response(status_code=403)