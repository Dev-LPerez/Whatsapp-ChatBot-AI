# main.py (Versión Estable y Simplificada)

import os
import json
import requests
import sqlite3
import google.generativeai as genai
from fastapi import FastAPI, Request, Response

app = FastAPI()

# --- CONFIGURACIÓN SEGURA ---
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
ID_NUMERO_TELEFONO = os.getenv("ID_NUMERO_TELEFONO")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- CONFIGURACIÓN DE LA BASE DE DATOS (SIMPLIFICADA) ---
DB_NAME = "database.db"

def inicializar_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Tabla mucho más simple, sin estados de conversación complejos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        numero_telefono TEXT PRIMARY KEY,
        nombre TEXT,
        nivel INTEGER,
        reto_actual_enunciado TEXT,
        reto_actual_solucion TEXT,
        reto_actual_tipo TEXT
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

# --- FUNCIONES DE IA (PROMPTS REFORZADOS) ---

def generar_reto_con_ia(nivel, tipo_reto):
    if not GEMINI_API_KEY: return {"error": "IA no configurada."}
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Genera un reto de programación de nivel {nivel} para **{tipo_reto}**.
    Tu respuesta DEBE ser un objeto JSON válido con "enunciado" y "solucion_ideal".
    - "enunciado": El texto del reto, pidiendo la solución en {tipo_reto}.
    - "solucion_ideal": La solución ejemplar en {tipo_reto}.
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.strip().replace("```json", "").replace("```", ""))
    except Exception as e:
        print(f"Error al generar reto con IA: {e}")
        return {"error": "No pude generar un reto."}

def evaluar_solucion_con_ia(reto_enunciado, solucion_usuario, tipo_reto):
    if not GEMINI_API_KEY: return "INCORRECTO: La evaluación no está configurada."
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    **Tarea Estricta:** Evalúa si la solución del estudiante resuelve el problema.
    **Problema:** "{reto_enunciado}"
    **Solución del Estudiante ({tipo_reto}):** "{solucion_usuario}"
    **Instrucciones:** Si la solución es irrelevante al problema, es "INCORRECTO". Tu respuesta DEBE empezar con "CORRECTO:" o "INCORRECTO:", seguido por un feedback conciso.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"INCORRECTO: Hubo un problema con el tutor de IA. {e}"

def chat_conversacional_con_ia(mensaje_usuario, reto_actual_solucion=None):
    if not GEMINI_API_KEY: return "Lo siento, el chat no está disponible."
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres "LogicBot", un tutor de programación.
    **Comandos Principales:** `reto python`, `reto java`, `reto pseudocodigo`, `solucion: [tu respuesta]`, `me rindo`.
    **Reglas:**
    1.  **Guía al Usuario:** Si el usuario parece perdido, recuérdale los comandos.
    2.  **Ayuda con Dudas:** Responde preguntas sobre programación.
    3.  **Si se Rinde (Instrucción Estricta):** Si el usuario dice "me rindo" y hay una solución (`{reto_actual_solucion}`), entrégala directamente sin hacer más preguntas.
    4.  **Mantente Enfocado:** Rechaza amablemente temas no relacionados.
    **Mensaje del usuario:** "{mensaje_usuario}"
    **Tu respuesta:**
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "No estoy seguro de cómo responder. Intenta con un comando como `reto python`."

# --- FUNCIÓN PARA ENVIAR MENSAJES ---
def responder_mensaje(numero_destinatario, texto_respuesta):
    if not WHATSAPP_TOKEN or not ID_NUMERO_TELEFONO:
        return
    url = f"https://graph.facebook.com/v19.0/{ID_NUMERO_TELEFONO}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": numero_destinatario, "text": {"body": texto_respuesta}}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar mensaje: {e}")

# --- WEBHOOK (LÓGICA PRINCIPAL SIMPLIFICADA) ---
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

        usuario = obtener_usuario(numero_remitente)

        if not usuario:
            crear_usuario(numero_remitente, nombre_usuario)
            bienvenida = (
                f"¡Hola, {nombre_usuario}! 👋 Soy LogicBot, tu tutor de IA.\n\n"
                "Estoy listo para ayudarte a practicar. Pídeme un reto cuando quieras con uno de estos comandos:\n"
                "- `reto python`\n"
                "- `reto java`\n"
                "- `reto pseudocodigo`"
            )
            responder_mensaje(numero_remitente, bienvenida)
            return Response(status_code=200)

        mensaje_lower = mensaje_texto.lower()

        if mensaje_lower.startswith("reto"):
            tipo_reto = None
            if "python" in mensaje_lower: tipo_reto = "Python"
            elif "java" in mensaje_lower: tipo_reto = "Java"
            elif "pseudo" in mensaje_lower: tipo_reto = "Pseudocódigo"
            
            if tipo_reto:
                responder_mensaje(numero_remitente, f"¡Entendido! Buscando un reto de {tipo_reto} (Nivel {usuario['nivel']})...")
                reto = generar_reto_con_ia(usuario['nivel'], tipo_reto)
                if "error" in reto:
                    responder_mensaje(numero_remitente, reto["error"])
                else:
                    actualizar_usuario(numero_remitente, {
                        "reto_actual_enunciado": reto["enunciado"],
                        "reto_actual_solucion": reto["solucion_ideal"],
                        "reto_actual_tipo": tipo_reto
                    })
                    responder_mensaje(numero_remitente, reto["enunciado"])
            else:
                responder_mensaje(numero_remitente, "No especificaste un lenguaje válido. Prueba con `reto python`, `reto java` o `reto pseudocodigo`.")

        elif mensaje_lower.startswith("solucion:"):
            if not usuario.get("reto_actual_enunciado"):
                responder_mensaje(numero_remitente, "No tienes un reto activo para resolver. ¡Pide uno nuevo!")
            else:
                solucion_usuario = mensaje_texto[len("solucion:"):].strip()
                feedback = evaluar_solucion_con_ia(usuario["reto_actual_enunciado"], solucion_usuario, usuario["reto_actual_tipo"])
                responder_mensaje(numero_remitente, feedback)
                if feedback.strip().upper().startswith("CORRECTO"):
                    nuevo_nivel = usuario["nivel"] + 1
                    actualizar_usuario(numero_remitente, {"nivel": nuevo_nivel, "reto_actual_enunciado": None, "reto_actual_solucion": None, "reto_actual_tipo": None})
                    responder_mensaje(numero_remitente, f"¡Felicidades! Has avanzado al nivel {nuevo_nivel}. Pide tu próximo reto cuando quieras.")

        elif mensaje_lower == "me rindo":
             if not usuario.get("reto_actual_solucion"):
                responder_mensaje(numero_remitente, "No tienes ningún reto activo para rendirte. ¡Pide uno!")
             else:
                respuesta = f"¡No te preocupes! La práctica hace al maestro. Aquí tienes la solución:\n\n```\n{usuario['reto_actual_solucion']}\n```\n\nAnalízala y pide otro reto cuando estés listo."
                actualizar_usuario(numero_remitente, {"reto_actual_enunciado": None, "reto_actual_solucion": None, "reto_actual_tipo": None})
                responder_mensaje(numero_remitente, respuesta)
        
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

@app.get("/webhook")
async def verificar_webhook(request: Request):
    VERIFY_TOKEN = "micodigosecreto"
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode and token and mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, status_code=200)
    return Response(status_code=403)