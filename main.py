# main.py (Corregido)

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
        estado_conversacion TEXT,
        tipo_reto_actual TEXT,
        ultimo_reto_diario TEXT,
        reto_actual_titulo TEXT,
        reto_actual_enunciado TEXT,
        reto_actual_solucion TEXT,
        ultimo_mensaje_bot TEXT
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

# --- FUNCIONES DE IA (sin cambios en esta corrección) ---
def generar_reto_con_ia(nivel, tipo_reto, historial_retos=[]):
    if not GEMINI_API_KEY:
        return {"error": "IA no configurada."}
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres un generador de retos de programación para un estudiante de nivel {nivel} en el formato **{tipo_reto}**.
    El usuario ya ha resuelto retos sobre los siguientes temas: {', '.join(historial_retos)}. **NO repitas estas temáticas.** Genera un reto nuevo y creativo.
    Tu respuesta DEBE ser un objeto JSON válido con "titulo", "enunciado" y "solucion_ideal".
    """
    try:
        response = model.generate_content(prompt)
        json_response = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
        return json_response
    except Exception as e:
        print(f"Error al generar reto con IA: {e}")
        return {"error": "No pude generar un reto en este momento."}

def evaluar_solucion_con_ia(reto_enunciado, solucion_usuario, tipo_reto):
    # (Esta función no necesita cambios)
    pass

def chat_conversacional_con_ia(mensaje_usuario, estado_conversacion, ultimo_mensaje_bot=None, reto_actual_solucion=None):
    # (Esta función no necesita cambios)
    pass

# --- FUNCIÓN PARA ENVIAR MENSAJES ---
def responder_mensaje(numero_destinatario, texto_respuesta):
    actualizar_usuario(numero_destinatario, {"ultimo_mensaje_bot": texto_respuesta})
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

# --- LÓGICA DE MENÚS ---
def enviar_menu_principal(numero):
    texto_menu = "¡Estoy listo para ayudarte! ✨\n\nElige una opción:\n1️⃣. 🧠 Reto Diario\n2️⃣. 🏋️‍♂️ Retos de Práctica"
    responder_mensaje(numero, texto_menu)

def enviar_menu_tipo_reto(numero):
    texto_menu = "¡Excelente! ¿Cómo prefieres practicar?\n\nElige el formato:\n1️⃣. 📝 Pseudocódigo\n2️⃣. ☕ Java\n3️⃣. 🐍 Python"
    responder_mensaje(numero, texto_menu)

# --- WEBHOOK (LÓGICA PRINCIPAL CORREGIDA) ---
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
            responder_mensaje(numero_remitente, f"¡Hola, {nombre_usuario}! 👋 Soy LogicBot.")
            enviar_menu_principal(numero_remitente)
            return Response(status_code=200)

        estado = usuario.get("estado_conversacion", "menu_principal")

        # --- MÁQUINA DE ESTADOS (CORREGIDA) ---
        if estado == 'menu_principal':
            if '1' in mensaje_texto or 'diario' in mensaje_texto.lower():
                actualizar_usuario(numero_remitente, {"estado_conversacion": "eligiendo_tipo_reto", "tipo_reto_actual": "diario"})
                enviar_menu_tipo_reto(numero_remitente)
            elif '2' in mensaje_texto or 'práctica' in mensaje_texto.lower():
                actualizar_usuario(numero_remitente, {"estado_conversacion": "eligiendo_tipo_reto", "tipo_reto_actual": "practica"})
                enviar_menu_tipo_reto(numero_remitente)
            else:
                respuesta_chat = chat_conversacional_con_ia(mensaje_texto, estado, usuario.get("ultimo_mensaje_bot"))
                responder_mensaje(numero_remitente, respuesta_chat)

        elif estado == 'eligiendo_tipo_reto':
            tipo_reto_formato = None
            if '1' in mensaje_texto or 'pseudo' in mensaje_texto.lower(): tipo_reto_formato = 'Pseudocódigo'
            elif '2' in mensaje_texto or 'java' in mensaje_texto.lower(): tipo_reto_formato = 'Java'
            elif '3' in mensaje_texto or 'python' in mensaje_texto.lower(): tipo_reto_formato = 'Python'
            
            if tipo_reto_formato:
                es_diario = usuario.get("tipo_reto_actual") == "diario"
                hoy = str(date.today())

                if es_diario and usuario.get("ultimo_reto_diario") == hoy:
                    responder_mensaje(numero_remitente, "Ya has completado tu reto diario de hoy. ¡Vuelve mañana!")
                    actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal"})
                    enviar_menu_principal(numero_remitente)
                    return Response(status_code=200)

                responder_mensaje(numero_remitente, f"¡Perfecto! Generando un reto de {tipo_reto_formato}...")
                reto = generar_reto_con_ia(usuario['nivel'], tipo_reto_formato)
                if "error" in reto:
                    responder_mensaje(numero_remitente, reto["error"])
                    actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal"})
                    enviar_menu_principal(numero_remitente)
                else:
                    actualizaciones = {
                        "estado_conversacion": "resolviendo_reto",
                        "tipo_reto_actual": tipo_reto_formato,
                        "reto_actual_titulo": reto["titulo"],
                        "reto_actual_enunciado": reto["enunciado"],
                        "reto_actual_solucion": reto["solucion_ideal"]
                    }
                    if es_diario:
                        actualizaciones["ultimo_reto_diario"] = hoy
                    actualizar_usuario(numero_remitente, actualizaciones)
                    responder_mensaje(numero_remitente, reto["enunciado"])
            else:
                respuesta_chat = chat_conversacional_con_ia(mensaje_texto, estado, usuario.get("ultimo_mensaje_bot"))
                responder_mensaje(numero_remitente, respuesta_chat)

        elif estado == 'resolviendo_reto':
            if mensaje_texto.lower().startswith("solucion:"):
                solucion_usuario = mensaje_texto[len("solucion:"):].strip()
                feedback = evaluar_solucion_con_ia(usuario["reto_actual_enunciado"], solucion_usuario, usuario["tipo_reto_actual"])
                responder_mensaje(numero_remitente, feedback)
                if feedback.strip().upper().startswith("CORRECTO"):
                    nuevo_nivel = usuario["nivel"] + 1
                    actualizar_usuario(numero_remitente, {"nivel": nuevo_nivel, "estado_conversacion": "menu_principal"})
                    responder_mensaje(numero_remitente, f"\n¡Felicidades, {usuario['nombre']}! ✨ Has avanzado al nivel {nuevo_nivel}.")
                    enviar_menu_principal(numero_remitente)
            else:
                respuesta_chat = chat_conversacional_con_ia(mensaje_texto, estado, usuario.get("ultimo_mensaje_bot"), usuario.get("reto_actual_solucion"))
                responder_mensaje(numero_remitente, respuesta_chat)

    except Exception as e:
        print(f"Ocurrió un error no manejado: {e}")
        pass
    return Response(status_code=200)

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