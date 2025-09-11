# main.py

import os
import json
import requests
import sqlite3
import google.generativeai as genai
from fastapi import FastAPI, Request, Response
from datetime import date

app = FastAPI()

# --- CONFIGURACIÓN SEGURA ---
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
ID_NUMERO_TELEFONO = os.getenv("ID_NUMERO_TELEFONO")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- CONFIGURACIÓN DE LA BASE DE DATOS (ACTUALIZADA) ---
DB_NAME = "database.db"

def inicializar_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Nueva tabla con estado de conversación y tipo de reto
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        numero_telefono TEXT PRIMARY KEY,
        nombre TEXT,
        nivel INTEGER,
        estado_conversacion TEXT,
        tipo_reto_actual TEXT,
        ultimo_reto_diario TEXT,
        reto_actual_enunciado TEXT,
        reto_actual_solucion TEXT
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
    if usuario:
        return dict(usuario)
    return None

def crear_usuario(numero_telefono, nombre):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # El estado inicial es 'menu_principal'
    cursor.execute("INSERT INTO usuarios (numero_telefono, nombre, nivel, estado_conversacion) VALUES (?, ?, ?, ?)", 
                   (numero_telefono, nombre, 1, 'menu_principal'))
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

# --- FUNCIONES DE IA (MEJORADAS) ---

def generar_reto_con_ia(nivel, tipo_reto):
    if not GEMINI_API_KEY:
        return {"error": "IA no configurada."}
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres un generador de retos de programación para un estudiante de nivel {nivel}.
    El reto debe ser para el lenguaje o formato: **{tipo_reto}**.
    - Si es 'Pseudocódigo', el reto debe pedir una solución en pseudocódigo.
    - Si es 'Java' o 'Python', el reto debe ser un problema de código que se pueda resolver con una función o un pequeño script en ese lenguaje.

    Tu respuesta DEBE ser un objeto JSON con "enunciado" y "solucion_ideal".
    - "enunciado": El texto completo del reto, pidiendo la solución en el lenguaje correcto.
    - "solucion_ideal": Una solución ejemplar en {tipo_reto}.
    """
    try:
        response = model.generate_content(prompt)
        json_response = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
        return json_response
    except Exception as e:
        print(f"Error al generar reto con IA: {e}")
        return {"error": "No pude generar un reto en este momento."}

def evaluar_solucion_con_ia(reto_enunciado, solucion_usuario, tipo_reto):
    if not GEMINI_API_KEY:
        return "INCORRECTO: La evaluación no está configurada."
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres un tutor de programación evaluando una solución en **{tipo_reto}**.
    - Tarea: "{reto_enunciado}"
    - Solución del estudiante: "{solucion_usuario}"

    Evalúa la solución. Responde en español, empezando con "CORRECTO:" o "INCORRECTO:", y da un feedback breve y útil.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"INCORRECTO: Hubo un problema con el tutor de IA. Error: {e}"

def chat_conversacional_con_ia(mensaje_usuario, reto_actual_solucion=None):
    if not GEMINI_API_KEY:
        return "Lo siento, el chat no está disponible."
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres "LogicBot", un tutor de programación amigable y experto.
    **Reglas:**
    1.  **Tu Propósito:** Ayudar a los usuarios a mejorar su lógica de programación.
    2.  **Guía al Usuario:** Explica cómo funcionas (menús, retos, etc.). Si te preguntan cómo responder, explica el formato `solucion: [tu respuesta]`.
    3.  **Ayuda con Dudas:** Si el usuario tiene una duda de programación, explícasela de forma sencilla.
    4.  **Si se Rinde:** Si el usuario dice "me rindo", "no sé", o pide la solución, y tienes una solución disponible, proporciónala con una explicación amigable. La solución es: `{reto_actual_solucion}`. Si no hay solución disponible, anímale a pedir un reto.
    5.  **Mantente Enfocado:** Rechaza amablemente preguntas no relacionadas con programación y redirige la conversación.

    **Pregunta del usuario:** "{mensaje_usuario}"
    **Tu respuesta:**
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "No estoy seguro de cómo responder. Intenta elegir una opción del menú."

# --- LÓGICA DE MENÚS ---
def enviar_menu_principal(numero):
    texto_menu = (
        "¡Estoy listo para ayudarte! ✨\n\n"
        "Elige una opción para empezar:\n"
        "1️⃣. 🧠 Reto Diario\n"
        "2️⃣. 🏋️‍♂️ Retos de Práctica"
    )
    responder_mensaje(numero, texto_menu)

def enviar_menu_tipo_reto(numero):
    texto_menu = (
        "¡Excelente! ¿Cómo prefieres practicar hoy?\n\n"
        "Elige el formato del reto:\n"
        "1️⃣. 📝 Pseudocódigo\n"
        "2️⃣. ☕ Java\n"
        "3️⃣. 🐍 Python"
    )
    responder_mensaje(numero, texto_menu)

# --- WEBHOOK (LÓGICA PRINCIPAL RECONSTRUIDA) ---
@app.post("/webhook")
async def recibir_mensaje(request: Request):
    body = await request.json()
    print(json.dumps(body, indent=2))

    try:
        # (Extracción de datos del mensaje, sin cambios)
        value = body['entry'][0]['changes'][0]['value']
        if not (value.get("messages") and value['messages'][0]):
            return Response(status_code=200) # Ignorar notificaciones de estado
        
        numero_remitente = value['messages'][0]['from']
        mensaje_texto = value['messages'][0]['text']['body']
        nombre_usuario = value['contacts'][0]['profile']['name']

        usuario = obtener_usuario(numero_remitente)

        if not usuario:
            crear_usuario(numero_remitente, nombre_usuario)
            responder_mensaje(numero_remitente, f"¡Hola, {nombre_usuario}! 👋 Soy LogicBot, tu tutor personal de programación.")
            enviar_menu_principal(numero_remitente)
            return Response(status_code=200)

        estado = usuario.get("estado_conversacion", "menu_principal")

        # --- MÁQUINA DE ESTADOS ---
        if estado == 'menu_principal':
            if '1' in mensaje_texto or 'diario' in mensaje_texto.lower():
                # Lógica del reto diario (simplificada por ahora)
                responder_mensaje(numero_remitente, "¡Genial! El reto diario estará disponible pronto. Por ahora, elige los retos de práctica.")
                enviar_menu_principal(numero_remitente) # Volvemos al menú
            elif '2' in mensaje_texto or 'práctica' in mensaje_texto.lower():
                actualizar_usuario(numero_remitente, {"estado_conversacion": "eligiendo_tipo_reto"})
                enviar_menu_tipo_reto(numero_remitente)
            else:
                enviar_menu_principal(numero_remitente)

        elif estado == 'eligiendo_tipo_reto':
            tipo_reto = None
            if '1' in mensaje_texto or 'pseudo' in mensaje_texto.lower():
                tipo_reto = 'Pseudocódigo'
            elif '2' in mensaje_texto or 'java' in mensaje_texto.lower():
                tipo_reto = 'Java'
            elif '3' in mensaje_texto or 'python' in mensaje_texto.lower():
                tipo_reto = 'Python'
            
            if tipo_reto:
                responder_mensaje(numero_remitente, f"¡Perfecto! Generando un reto de {tipo_reto} para tu nivel ({usuario['nivel']})...")
                reto = generar_reto_con_ia(usuario['nivel'], tipo_reto)
                if "error" in reto:
                    responder_mensaje(numero_remitente, reto["error"])
                    actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal"})
                    enviar_menu_principal(numero_remitente)
                else:
                    actualizar_usuario(numero_remitente, {
                        "estado_conversacion": "resolviendo_reto",
                        "tipo_reto_actual": tipo_reto,
                        "reto_actual_enunciado": reto["enunciado"],
                        "reto_actual_solucion": reto["solucion_ideal"]
                    })
                    responder_mensaje(numero_remitente, reto["enunciado"])
            else:
                responder_mensaje(numero_remitente, "No reconocí esa opción. Por favor, elige una de las disponibles.")
                enviar_menu_tipo_reto(numero_remitente)

        elif estado == 'resolviendo_reto':
            if mensaje_texto.lower().startswith("solucion:"):
                solucion_usuario = mensaje_texto[len("solucion:"):].strip()
                feedback = evaluar_solucion_con_ia(usuario["reto_actual_enunciado"], solucion_usuario, usuario["tipo_reto_actual"])
                responder_mensaje(numero_remitente, feedback)
                if feedback.strip().upper().startswith("CORRECTO"):
                    nuevo_nivel = usuario["nivel"] + 1
                    actualizar_usuario(numero_remitente, {"nivel": nuevo_nivel, "estado_conversacion": "menu_principal"})
                    responder_mensaje(numero_remitente, f"\n¡Felicidades! Has avanzado al nivel {nuevo_nivel}.")
                    enviar_menu_principal(numero_remitente)
            else:
                respuesta_chat = chat_conversacional_con_ia(mensaje_texto, usuario.get("reto_actual_solucion"))
                responder_mensaje(numero_remitente, respuesta_chat)

    except Exception as e:
        print(f"Ocurrió un error no manejado: {e}")
        pass
    return Response(status_code=200)

# --- El resto de funciones se mantienen igual ---
@app.on_event("startup")
async def startup_event():
    inicializar_db()

def responder_mensaje(numero_destinatario, texto_respuesta):
    # (Esta función se queda igual)
    if not WHATSAPP_TOKEN or not ID_NUMERO_TELEFONO:
        print("ERROR: Faltan las variables de entorno de WhatsApp.")
        return
    url = f"https://graph.facebook.com/v19.0/{ID_NUMERO_TELEFONO}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": numero_destinatario, "text": {"body": texto_respuesta}}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar mensaje: {e}")

@app.get("/webhook")
async def verificar_webhook(request: Request):
    # (Esta función se queda igual)
    VERIFY_TOKEN = "micodigosecreto"
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode and token and mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, status_code=200)
    return Response(status_code=403)