# main.py

import os
import json
import requests
import sqlite3
import google.generativeai as genai
from fastapi import FastAPI, Request, Response
from datetime import date

app = FastAPI()

# --- IMPORTANTE: CONFIGURACIÓN SEGURA ---
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
ID_NUMERO_TELEFONO = os.getenv("ID_NUMERO_TELEFONO")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
DB_NAME = "database.db"

def inicializar_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        numero_telefono TEXT PRIMARY KEY,
        nombre TEXT,
        nivel INTEGER,
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
    cursor.execute("INSERT INTO usuarios (numero_telefono, nombre, nivel) VALUES (?, ?, ?)", (numero_telefono, nombre, 1))
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

# --- FUNCIONES DE IA ---

def generar_reto_con_ia(nivel):
    if not GEMINI_API_KEY:
        return {"error": "La función de IA no está configurada."}
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres un generador de retos de lógica de programación. Tu tarea es crear un desafío para un estudiante de nivel {nivel}.
    El nivel 1 son fundamentos básicos. Nivel 2 son condicionales. Nivel 3 son bucles. Niveles superiores son arrays, etc.
    Crea un reto apropiado para el nivel {nivel}.
    Tu respuesta DEBE ser un objeto JSON con "enunciado" y "solucion_ideal".
    """
    try:
        response = model.generate_content(prompt)
        json_response = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
        return json_response
    except Exception as e:
        print(f"Error al generar reto con IA: {e}")
        return {"error": "No pude generar un reto en este momento."}

def evaluar_solucion_con_ia(reto_enunciado, solucion_usuario):
    if not GEMINI_API_KEY:
        return "INCORRECTO: La función de evaluación no está configurada."
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f'Eres un tutor de programación. Evalúa la siguiente solución de pseudocódigo. Tarea: "{reto_enunciado}". Solución: "{solucion_usuario}". Responde en español, empezando con "CORRECTO:" o "INCORRECTO:", y da un feedback breve y útil.'
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error al llamar a la API de Gemini: {e}")
        return "INCORRECTO: Hubo un problema con el tutor de IA."

# --- NUEVA FUNCIÓN DE IA: CHAT CONVERSACIONAL ---
def chat_conversacional_con_ia(mensaje_usuario):
    if not GEMINI_API_KEY:
        return "Lo siento, la función de chat no está disponible en este momento."
        
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Eres "LogicBot", un tutor de programación experto, amigable y paciente. Tu único propósito es ayudar a los usuarios a mejorar su lógica de programación con retos.

    **Tus Reglas:**
    1.  **Preséntate:** Si te preguntan quién eres, eres LogicBot.
    2.  **Explica tu función:** Explica que ofreces retos diarios y de práctica.
    3.  **Guía al usuario:** Si te preguntan cómo enviar una solución, explícales claramente que deben escribir la palabra `solucion:` seguida de su respuesta en pseudocódigo.
    4.  **Mantente enfocado:** SOLO respondes preguntas sobre programación, lógica, retos o tu propio funcionamiento.
    5.  **Rechaza otros temas:** Si te preguntan sobre cualquier otra cosa (clima, política, deportes, etc.), debes rechazar amablemente la pregunta y redirigir la conversación a la programación. Ejemplo: "Esa es una pregunta interesante, pero mi especialidad es la lógica de programación. ¿Te gustaría intentar un reto?"

    **Pregunta del usuario:** "{mensaje_usuario}"

    **Tu respuesta (amigable, concisa y en español):**
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error en el chat conversacional con IA: {e}")
        return "No estoy seguro de cómo responder a eso. Recuerda que soy un bot de programación. Intenta pedir un 'reto diario'."

# --- WEBHOOK (LÓGICA PRINCIPAL ACTUALIZADA) ---
@app.post("/webhook")
async def recibir_mensaje(request: Request):
    body = await request.json()
    print(json.dumps(body, indent=2))

    try:
        if (body.get("entry") and body['entry'][0].get("changes") and
                body['entry'][0]['changes'][0].get("value") and
                body['entry'][0]['changes'][0]['value'].get("messages") and
                body['entry'][0]['changes'][0]['value']['messages'][0]):

            value = body['entry'][0]['changes'][0]['value']
            numero_remitente = value['messages'][0]['from']
            mensaje_texto = value['messages'][0]['text']['body']
            nombre_usuario = value['contacts'][0]['profile']['name']

            usuario_actual = obtener_usuario(numero_remitente)

            if not usuario_actual:
                crear_usuario(numero_remitente, nombre_usuario)
                texto_respuesta = f"¡Hola, {nombre_usuario}! 👋 Soy LogicBot, tu tutor de programación. Escribe 'reto diario' para empezar tu primer desafío."
                responder_mensaje(numero_remitente, texto_respuesta)
                return Response(status_code=200)

            mensaje_lower = mensaje_texto.lower()

            if mensaje_texto.lower().startswith("solucion:"):
                solucion_usuario = mensaje_texto[len("solucion:"):].strip()
                if not usuario_actual.get("reto_actual_enunciado"):
                    responder_mensaje(numero_remitente, "No tienes un reto activo. Pide uno nuevo escribiendo 'reto diario' o 'reto de práctica'.")
                else:
                    feedback_ia = evaluar_solucion_con_ia(usuario_actual["reto_actual_enunciado"], solucion_usuario)
                    responder_mensaje(numero_remitente, feedback_ia)
                    if feedback_ia.strip().upper().startswith("CORRECTO"):
                        nuevo_nivel = usuario_actual["nivel"] + 1
                        actualizar_usuario(numero_remitente, {"nivel": nuevo_nivel, "reto_actual_enunciado": None, "reto_actual_solucion": None})
                        agradecimiento = f"\n\n¡Excelente! Has avanzado al nivel {nuevo_nivel}. ¡Sigue así!"
                        responder_mensaje(numero_remitente, agradecimiento)

            elif "reto diario" in mensaje_lower:
                hoy = str(date.today())
                if usuario_actual.get("ultimo_reto_diario") == hoy:
                    responder_mensaje(numero_remitente, "Ya has recibido tu reto diario de hoy. ¡Intenta resolverlo! Si quieres más, escribe 'reto de práctica'.")
                else:
                    responder_mensaje(numero_remitente, "¡Genial! Generando tu reto diario...")
                    reto = generar_reto_con_ia(usuario_actual["nivel"])
                    if "error" in reto:
                        responder_mensaje(numero_remitente, reto["error"])
                    else:
                        actualizar_usuario(numero_remitente, {"ultimo_reto_diario": hoy, "reto_actual_enunciado": reto["enunciado"], "reto_actual_solucion": reto["solucion_ideal"]})
                        responder_mensaje(numero_remitente, reto["enunciado"])
            
            elif "reto de práctica" in mensaje_lower:
                responder_mensaje(numero_remitente, "¡Claro! Buscando un reto de práctica para ti...")
                reto = generar_reto_con_ia(usuario_actual["nivel"])
                if "error" in reto:
                    responder_mensaje(numero_remitente, reto["error"])
                else:
                    actualizar_usuario(numero_remitente, {"reto_actual_enunciado": reto["enunciado"], "reto_actual_solucion": reto["solucion_ideal"]})
                    responder_mensaje(numero_remitente, reto["enunciado"])

            else:
                # --- ACTUALIZACIÓN: Si no es un comando, usamos el chat de IA ---
                respuesta_chat = chat_conversacional_con_ia(mensaje_texto)
                responder_mensaje(numero_remitente, respuesta_chat)

    except Exception as e:
        print(f"Ocurrió un error no manejado: {e}")
        pass

    return Response(status_code=200)

# --- Se ejecuta una sola vez al iniciar el servidor ---
@app.on_event("startup")
async def startup_event():
    inicializar_db()

# --- FUNCIONES RESTANTES (sin cambios) ---
def responder_mensaje(numero_destinatario, texto_respuesta):
    if not WHATSAPP_TOKEN or not ID_NUMERO_TELEFONO:
        print("ERROR: Faltan las variables de entorno de WhatsApp.")
        return
    url = f"https://graph.facebook.com/v19.0/{ID_NUMERO_TELEFONO}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": numero_destinatario, "text": {"body": texto_respuesta}}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Respuesta de la API de Meta: {response.status_code}")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar mensaje: {e}")

@app.get("/webhook")
async def verificar_webhook(request: Request):
    VERIFY_TOKEN = "micodigosecreto"
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode and token and mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK_VERIFIED")
        return Response(content=challenge, status_code=200)
    return Response(status_code=403)