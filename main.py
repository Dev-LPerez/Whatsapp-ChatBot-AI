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
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        numero_telefono TEXT PRIMARY KEY,
        nombre TEXT,
        nivel INTEGER,
        ultimo_reto_diario TEXT,
        reto_actual_enunciado TEXT,
        reto_actual_solucion TEXT,
        historial_retos TEXT
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
    # El historial se inicializa como una lista JSON vacía
    cursor.execute("INSERT INTO usuarios (numero_telefono, nombre, nivel, historial_retos) VALUES (?, ?, ?, ?)", (numero_telefono, nombre, 1, json.dumps([])))
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

# --- ACTUALIZADO: GENERADOR DE RETOS CON MEMORIA Y TEMÁTICA ---
def generar_reto_con_ia(nivel, tematica=None, historial_retos=[]):
    if not GEMINI_API_KEY:
        return {"error": "La función de IA no está configurada."}
        
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Construcción dinámica del prompt
    prompt = f"Eres un generador de retos de lógica de programación para un estudiante de nivel {nivel}.\n"
    
    if tematica:
        prompt += f"El reto DEBE estar relacionado con la siguiente temática: '{tematica}'.\n"
        
    if historial_retos:
        historial_str = ", ".join(historial_retos)
        prompt += f"El usuario ya ha resuelto retos sobre: {historial_str}. NO generes un reto con una temática idéntica o muy similar a estos.\n"
        
    prompt += """
    Tu respuesta DEBE ser un objeto JSON con tres claves: "titulo", "enunciado" y "solucion_ideal".
    - "titulo": Un título corto para el reto (ej: "Calcular Área de Rectángulo").
    - "enunciado": El texto completo del reto.
    - "solucion_ideal": Una solución ejemplar en pseudocódigo.
    """
    
    try:
        response = model.generate_content(prompt)
        json_response = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
        return json_response
    except Exception as e:
        print(f"Error al generar reto con IA: {e}")
        return {"error": "No pude generar un reto en este momento. Intenta de nuevo."}

def evaluar_solucion_con_ia(reto_enunciado, solucion_usuario):
    # (Sin cambios)
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

def chat_conversacional_con_ia(mensaje_usuario):
    # (Sin cambios)
    if not GEMINI_API_KEY:
        return "Lo siento, la función de chat no está disponible."
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f'Eres "LogicBot", un tutor de programación. Tu único propósito es ayudar a los usuarios con retos de lógica. Si te preguntan cómo enviar soluciones, diles que usen `solucion: [respuesta]`. Si te preguntan algo fuera de tema, redirige amablemente a la programación. Pregunta del usuario: "{mensaje_usuario}". Tu respuesta (amigable y concisa):'
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error en el chat conversacional con IA: {e}")
        return "No estoy seguro de cómo responder a eso. Intenta pedir un 'reto diario'."

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
                texto_respuesta = f"¡Hola, {nombre_usuario}! 👋 Soy LogicBot, tu tutor de programación. Escribe 'reto diario' para empezar."
                responder_mensaje(numero_remitente, texto_respuesta)
                return Response(status_code=200)

            mensaje_lower = mensaje_texto.lower()
            historial_retos_json = usuario_actual.get("historial_retos", "[]")
            historial_retos = json.loads(historial_retos_json)

            if mensaje_texto.lower().startswith("solucion:"):
                solucion_usuario = mensaje_texto[len("solucion:"):].strip()
                if not usuario_actual.get("reto_actual_enunciado"):
                    responder_mensaje(numero_remitente, "No tienes un reto activo. Pide uno nuevo.")
                else:
                    feedback_ia = evaluar_solucion_con_ia(usuario_actual["reto_actual_enunciado"], solucion_usuario)
                    responder_mensaje(numero_remitente, feedback_ia)
                    if feedback_ia.strip().upper().startswith("CORRECTO"):
                        nuevo_nivel = usuario_actual["nivel"] + 1
                        historial_retos.append(usuario_actual.get("reto_actual_titulo", "Reto completado")) # Guardamos el título del reto
                        actualizar_usuario(numero_remitente, {"nivel": nuevo_nivel, "reto_actual_enunciado": None, "reto_actual_solucion": None, "historial_retos": json.dumps(historial_retos[-5:])}) # Guardamos los últimos 5
                        agradecimiento = f"\n\n¡Excelente! Has avanzado al nivel {nuevo_nivel}. ¡Sigue así!"
                        responder_mensaje(numero_remitente, agradecimiento)

            elif "reto diario" in mensaje_lower or "reto de práctica" in mensaje_lower:
                hoy = str(date.today())
                if "reto diario" in mensaje_lower and usuario_actual.get("ultimo_reto_diario") == hoy:
                    responder_mensaje(numero_remitente, "Ya has recibido tu reto diario de hoy. Si quieres más, escribe 'reto de práctica'.")
                    return Response(status_code=200)

                # Extracción simple de temática
                tematica = None
                if "sobre" in mensaje_lower:
                    try:
                        tematica = mensaje_texto.split("sobre", 1)[1].strip()
                    except IndexError:
                        pass

                responder_mensaje(numero_remitente, f"¡Entendido! Buscando un reto para ti{f' sobre {tematica}' if tematica else ''}...")
                reto = generar_reto_con_ia(usuario_actual["nivel"], tematica, historial_retos)
                
                if "error" in reto:
                    responder_mensaje(numero_remitente, reto["error"])
                else:
                    actualizaciones = {
                        "reto_actual_titulo": reto["titulo"],
                        "reto_actual_enunciado": reto["enunciado"],
                        "reto_actual_solucion": reto["solucion_ideal"]
                    }
                    if "reto diario" in mensaje_lower:
                        actualizaciones["ultimo_reto_diario"] = hoy
                    
                    actualizar_usuario(numero_remitente, actualizaciones)
                    responder_mensaje(numero_remitente, reto["enunciado"])
            else:
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
        print(f"Respuesta de la API de Meta: {response.status_code}")
        print(response.json())
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
        print("WEBHOOK_VERIFIED")
        return Response(content=challenge, status_code=200)
    return Response(status_code=403)