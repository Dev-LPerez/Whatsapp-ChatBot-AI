# main.py (LogicBot v3.0 - El Tutor Definitivo)

import os
import json
import requests
import sqlite3
import google.generativeai as genai
from fastapi import FastAPI, Request, Response
from datetime import date, datetime

app = FastAPI()

# --- CONFIGURACIÓN SEGURA ---
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
ID_NUMERO_TELEFONO = os.getenv("ID_NUMERO_TELEFONO")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- CONFIGURACIÓN DE LA BASE DE DATOS (v3.0) ---
DB_NAME = "database.db"

def inicializar_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Tabla final con gamificación y memoria conversacional
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        numero_telefono TEXT PRIMARY KEY,
        nombre TEXT,
        nivel INTEGER DEFAULT 1,
        puntos INTEGER DEFAULT 0,
        racha_dias INTEGER DEFAULT 0,
        ultima_conexion TEXT,
        estado_conversacion TEXT,
        reto_actual_enunciado TEXT,
        reto_actual_solucion TEXT,
        reto_actual_tipo TEXT,
        reto_actual_pistas TEXT,
        pistas_usadas INTEGER DEFAULT 0,
        historial_chat TEXT
    )
    """)
    conn.commit()
    conn.close()

# --- FUNCIONES DE BASE DE DATOS ---
def obtener_usuario(numero_telefono):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE numero_telefono = ?", (numero_telefono,))
    usuario = cursor.fetchone()
    conn.close()
    return dict(usuario) if usuario else None

def crear_usuario(numero_telefono, nombre):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    hoy = str(date.today())
    cursor.execute(
        "INSERT INTO usuarios (numero_telefono, nombre, estado_conversacion, ultima_conexion, historial_chat) VALUES (?, ?, ?, ?, ?)",
        (numero_telefono, nombre, 'menu_principal', hoy, json.dumps([]))
    )
    conn.commit()
    conn.close()

def actualizar_usuario(numero_telefono, datos):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    campos = ", ".join([f"{key} = ?" for key in datos.keys()])
    valores = list(datos.values())
    valores.append(numero_telefono)
    cursor.execute(f"UPDATE usuarios SET {campos} WHERE numero_telefono = ?", tuple(valores))
    conn.commit()
    conn.close()

# --- FUNCIONES DE IA (PROMPTS AVANZADOS) ---
def generar_reto_con_ia(nivel, tipo_reto, dificultad, tematica=None):
    if not GEMINI_API_KEY: return {"error": "IA no configurada."}
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres un generador de retos de programación experto.
    Crea un reto de nivel {nivel}, con dificultad **{dificultad}**, para el lenguaje/formato **{tipo_reto}**.
    {f"El reto debe tratar sobre: '{tematica}'." if tematica else ""}
    
    Tu respuesta DEBE ser un objeto JSON válido con "enunciado", "solucion_ideal" y "pistas".
    - "enunciado": El texto del reto, con título en negrita y emojis.
    - "solucion_ideal": La solución ejemplar.
    - "pistas": Un array de 3 strings con pistas progresivas, de la más sutil a la más obvia.
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.strip().replace("```json", "").replace("```", ""))
    except Exception as e:
        return {"error": f"No pude generar el reto. Error de IA: {e}"}

def evaluar_solucion_con_ia(reto_enunciado, solucion_usuario, tipo_reto):
    # (Sin cambios, el prompt ya es robusto)
    pass 

def chat_conversacional_con_ia(mensaje_usuario, historial_chat, reto_actual_solucion=None):
    if not GEMINI_API_KEY: return "Lo siento, el chat no está disponible."
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres "LogicBot", un tutor de programación amigable.
    **Historial de Conversación (últimos 4 mensajes):** {historial_chat}
    **Mensaje actual del usuario:** "{mensaje_usuario}"

    **Reglas:**
    1.  **Usa el Contexto:** Responde basándote en el historial para que la conversación sea fluida.
    2.  **Guía y Ayuda:** Explica comandos (`reto python`, `mi perfil`, etc.) y conceptos de programación.
    3.  **Si se Rinde (Instrucción Estricta):** Si el usuario dice `me rindo` o pide la solución, y tienes una (`{reto_actual_solucion}`), entrégala con una explicación detallada de cómo funciona.
    
    **Tu respuesta:**
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "No estoy seguro de cómo responder. Intenta con un comando como `reto python`."

# --- FUNCIÓN PARA ENVIAR MENSAJES Y ACTUALIZAR HISTORIAL ---
def responder_mensaje(numero_destinatario, texto_respuesta, historial_actual=[]):
    if not WHATSAPP_TOKEN or not ID_NUMERO_TELEFONO: return
    
    # Actualizamos el historial de chat
    nuevo_historial = historial_actual + [{"bot": texto_respuesta}]
    actualizar_usuario(numero_destinatario, {"historial_chat": json.dumps(nuevo_historial[-4:])}) # Guardamos los últimos 4 mensajes
    
    url = f"https://graph.facebook.com/v19.0/{ID_NUMERO_TELEFONO}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": numero_destinatario, "text": {"preview_url": False, "body": texto_respuesta}}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar mensaje: {e}")

# --- WEBHOOK (LÓGICA PRINCIPAL CON TODAS LAS MEJORAS) ---
@app.post("/webhook")
async def recibir_mensaje(request: Request):
    body = await request.json()
    print(json.dumps(body, indent=2))

    try:
        value = body['entry'][0]['changes'][0]['value']
        if not (value.get("messages") and value['messages'][0]): return Response(status_code=200)
        
        numero_remitente = value['messages'][0]['from']
        mensaje_texto = value['messages'][0]['text']['body']
        nombre_usuario = value['contacts'][0]['profile']['name']

        usuario = obtener_usuario(numero_remitente)
        hoy_str = str(date.today())

        if not usuario:
            crear_usuario(numero_remitente, nombre_usuario)
            usuario = obtener_usuario(numero_remitente) # Recargamos para tener todos los datos
            bienvenida = (
                f"¡Hola, {nombre_usuario}! 👋 Soy LogicBot, tu tutor de IA personal.\n\n"
                "Estoy aquí para ayudarte a practicar y mejorar tu lógica de programación. ¡Vamos a empezar! 🚀\n\n"
                "**Comandos disponibles:**\n"
                "- `reto python` (o java/pseudocodigo)\n"
                "- `mi perfil` para ver tus estadísticas."
            )
            responder_mensaje(numero_remitente, bienvenida, [])
            return Response(status_code=200)
        
        # Actualizar racha de días
        if usuario.get("ultima_conexion") != hoy_str:
            ayer = date.fromisoformat(usuario.get("ultima_conexion", "1970-01-01"))
            racha = usuario.get("racha_dias", 0)
            if (date.today() - ayer).days == 1:
                racha += 1
            else:
                racha = 1 # Se rompió la racha, se reinicia
            actualizar_usuario(numero_remitente, {"ultima_conexion": hoy_str, "racha_dias": racha})

        historial_chat = json.loads(usuario.get("historial_chat", "[]"))
        historial_chat.append({"usuario": mensaje_texto})
        estado = usuario.get("estado_conversacion", "menu_principal")
        mensaje_lower = mensaje_texto.lower()

        if mensaje_lower.startswith("reto"):
            tipo_reto, tematica = None, None
            if "python" in mensaje_lower: tipo_reto = "Python"
            elif "java" in mensaje_lower: tipo_reto = "Java"
            elif "pseudo" in mensaje_lower: tipo_reto = "Pseudocodódigo"
            
            if "sobre" in mensaje_lower:
                tematica = mensaje_texto.split("sobre", 1)[1].strip()

            if tipo_reto:
                actualizar_usuario(numero_remitente, {
                    "estado_conversacion": "eligiendo_dificultad", 
                    "tipo_reto_actual": tipo_reto,
                    "tematica_actual": tematica # Guardamos la temática
                })
                responder_mensaje(numero_remitente, "¿Qué nivel de dificultad prefieres para tu reto? 🤔\n\n1. Fácil 🌱\n2. Intermedio 🔥\n3. Difícil 🤯", historial_chat)
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
                reto = generar_reto_con_ia(usuario['nivel'], tipo_reto, dificultad, tematica)

                if "error" in reto:
                    responder_mensaje(numero_remitente, reto["error"], historial_chat)
                    actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal"})
                else:
                    actualizar_usuario(numero_remitente, {
                        "estado_conversacion": "resolviendo_reto",
                        "reto_actual_enunciado": reto["enunciado"],
                        "reto_actual_solucion": reto["solucion_ideal"],
                        "reto_actual_pistas": json.dumps(reto["pistas"]),
                        "pistas_usadas": 0
                    })
                    responder_mensaje(numero_remitente, reto["enunciado"], historial_chat)
            else:
                responder_mensaje(numero_remitente, "Por favor, elige una dificultad: 1, 2 o 3.", historial_chat)

        elif mensaje_lower.startswith("solucion:"):
            if not usuario.get("reto_actual_enunciado"):
                responder_mensaje(numero_remitente, "¡Ups! 😅 No tienes un reto activo.", historial_chat)
            else:
                solucion_usuario = mensaje_texto[len("solucion:"):].strip()
                feedback = evaluar_solucion_con_ia(usuario["reto_actual_enunciado"], solucion_usuario, usuario["reto_actual_tipo"])
                responder_mensaje(numero_remitente, feedback, historial_chat)
                if feedback.strip().upper().startswith("✅"):
                    puntos_ganados = 10
                    nuevo_nivel = usuario["nivel"] + 1 if (usuario["puntos"] + puntos_ganados) % 100 == 0 else usuario["nivel"]
                    actualizar_usuario(numero_remitente, {
                        "puntos": usuario["puntos"] + puntos_ganados,
                        "nivel": nuevo_nivel,
                        "estado_conversacion": "menu_principal",
                        "reto_actual_enunciado": None
                    })
                    mensaje_felicitacion = f"Ganaste *{puntos_ganados} puntos*. ¡Sigue así!"
                    if nuevo_nivel > usuario["nivel"]:
                        mensaje_felicitacion += f"\n\n🚀 ¡FELICIDADES! ¡Has subido al Nivel {nuevo_nivel}!"
                    responder_mensaje(numero_remitente, mensaje_felicitacion, historial_chat)
        
        elif mensaje_lower == "pista":
            if not usuario.get("reto_actual_enunciado"):
                responder_mensaje(numero_remitente, "No tienes un reto activo para pedir una pista.", historial_chat)
            else:
                pistas = json.loads(usuario.get("reto_actual_pistas", "[]"))
                pistas_usadas = usuario.get("pistas_usadas", 0)
                if pistas_usadas < len(pistas):
                    responder_mensaje(numero_remitente, f"🔍 *Pista {pistas_usadas + 1}:* {pistas[pistas_usadas]}", historial_chat)
                    actualizar_usuario(numero_remitente, {"pistas_usadas": pistas_usadas + 1})
                else:
                    responder_mensaje(numero_remitente, "¡Ya has usado todas las pistas! 😥 Si quieres, puedes rendirte escribiendo `me rindo`.", historial_chat)
        
        elif mensaje_lower == "me rindo":
             if not usuario.get("reto_actual_solucion"):
                responder_mensaje(numero_remitente, "Tranquilo, no tienes ningún reto activo para rendirte.", historial_chat)
             else:
                respuesta_con_explicacion = chat_conversacional_con_ia(mensaje_texto, historial_chat, usuario.get("reto_actual_solucion"))
                actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal", "reto_actual_enunciado": None})
                responder_mensaje(numero_remitente, respuesta_con_explicacion, historial_chat)

        elif mensaje_lower == "mi perfil":
            perfil = (
                f"📊 *Tu Perfil de LogicBot*\n\n"
                f"👤 *Nombre:* {usuario['nombre']}\n"
                f"🎓 *Nivel:* {usuario['nivel']}\n"
                f"⭐ *Puntos:* {usuario['puntos']}\n"
                f"🔥 *Racha:* {usuario['racha_dias']} día(s)"
            )
            responder_mensaje(numero_remitente, perfil, historial_chat)

        else:
            respuesta_chat = chat_conversacional_con_ia(mensaje_texto, historial_chat, usuario.get("reto_actual_solucion"))
            responder_mensaje(numero_remitente, respuesta_chat, historial_chat)

    except Exception as e:
        print(f"Ocurrió un error no manejado: {e}")
        pass
    return Response(status_code=200)

# --- El resto de funciones se mantienen igual ---
@app.on_event("startup")
async def startup_event():
    inicializar_db()

@app.get("/webhook")
async def verificar_webhook(request: Request):
    VERIFY_TOKEN = "micodigosecreto"
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode and token and mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, status_code=200)
    return Response(status_code=403)