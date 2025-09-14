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

# --- CONFIGURACIÓN DE LA BASE DE DATOS (VERSIÓN FINAL) ---
DB_NAME = "database.db"

def inicializar_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Añadimos ultimo_mensaje_bot para el contexto conversacional
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

# --- FUNCIONES DE IA (PROMPTS MEJORADOS) ---

def generar_reto_con_ia(nivel, tipo_reto, historial_retos=[]):
    if not GEMINI_API_KEY:
        return {"error": "IA no configurada."}
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres un generador de retos de programación para un estudiante de nivel {nivel} en el formato **{tipo_reto}**.
    El usuario ya ha resuelto retos sobre los siguientes temas: {', '.join(historial_retos)}. **NO repitas estas temáticas.** Genera un reto nuevo y creativo.
    Tu respuesta DEBE ser un objeto JSON válido con "titulo", "enunciado" y "solucion_ideal".
    - "titulo": Título corto para el reto.
    - "enunciado": El texto completo del reto, pidiendo la solución en el formato correcto ({tipo_reto}).
    - "solucion_ideal": Una solución ejemplar y bien comentada.
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
    **Contexto:** Eres un tutor de programación estricto y preciso.
    **Tarea:** Evaluar si la solución de un estudiante resuelve el problema planteado.
    **Problema a Resolver:** "{reto_enunciado}"
    **Solución del Estudiante en {tipo_reto}:** "{solucion_usuario}"

    **Instrucciones de Evaluación:**
    1.  **Compara Estrictamente:** Tu única tarea es determinar si el código/pseudocódigo del estudiante resuelve el **Problema a Resolver** específico.
    2.  **Detecta Soluciones Irrelevantes:** Si el estudiante envía una solución que resuelve un problema diferente (aunque el código sea correcto para ese otro problema), tu respuesta DEBE ser "INCORRECTO".
    3.  **Formato de Respuesta Obligatorio:**
        -   Si la solución resuelve correctamente el problema, tu respuesta DEBE empezar con "CORRECTO:" seguido de un feedback positivo y constructivo.
        -   Si la solución NO resuelve el problema (ya sea por errores lógicos o por ser irrelevante), tu respuesta DEBE empezar con "INCORRECTO:" seguido de una pista clara que apunte al error principal.

    **Ejemplo de error:** Si el problema era "contar palíndromos" y el estudiante envió una función para "calcular promedio", tu respuesta debe ser: "INCORRECTO: Tu solución implementa una función para calcular un promedio, pero el reto solicitado era contar palíndromos. Asegúrate de que tu solución aborde el problema correcto."

    **Tu Evaluación:**
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"INCORRECTO: Hubo un problema con el tutor de IA. Error: {e}"

def chat_conversacional_con_ia(mensaje_usuario, estado_conversacion, ultimo_mensaje_bot=None, reto_actual_solucion=None):
    if not GEMINI_API_KEY:
        return "Lo siento, el chat no está disponible."
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres "LogicBot", un tutor de programación amigable y experto.
    **Contexto de la Conversación:**
    - El estado actual del usuario es: "{estado_conversacion}".
    - Tu último mensaje fue: "{ultimo_mensaje_bot}"
    - Mensaje actual del usuario: "{mensaje_usuario}"

    **Tus Reglas de Comportamiento:**
    1.  **Sé Contextual:** Si el mensaje del usuario parece una respuesta a tu último mensaje (ej: "no entendí"), responde basándote en ese contexto.
    2.  **Guía al Usuario:** Explica cómo funcionas (menús, retos, etc.). Si te preguntan cómo responder, explica el formato `solucion: [tu respuesta]`.
    3.  **Ayuda con Dudas:** Si el usuario tiene una duda de programación, explícasela de forma sencilla.
    4.  **Si se Rinde (Instrucción Estricta):** Si el usuario dice "me rindo", "no sé", "dame la solución" o algo similar, TU ÚNICA ACCIÓN es proporcionar la solución del reto actual de forma directa y amigable. La solución es: `{reto_actual_solucion}`. No hagas más preguntas, solo da la solución.
    5.  **Mantente Enfocado:** Rechaza amablemente preguntas no relacionadas con programación y redirige la conversación a tu propósito principal.
    
    **Tu respuesta (concisa y amigable):**
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "No estoy seguro de cómo responder. Intenta elegir una opción del menú."

# --- FUNCIÓN PARA ENVIAR MENSAJES (ACTUALIZADA) ---
def responder_mensaje(numero_destinatario, texto_respuesta):
    if not WHATSAPP_TOKEN or not ID_NUMERO_TELEFONO:
        print("ERROR: Faltan las variables de entorno de WhatsApp.")
        return
    # Actualizamos el último mensaje del bot en la DB para dar contexto a la IA
    actualizar_usuario(numero_destinatario, {"ultimo_mensaje_bot": texto_respuesta})
    
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
        value = body['entry'][0]['changes'][0]['value']
        if not (value.get("messages") and value['messages'][0]):
            return Response(status_code=200)
        
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

        # --- MÁQUINA DE ESTADOS (MÁS FLEXIBLE) ---
        if estado == 'menu_principal':
            if '1' in mensaje_texto or 'diario' in mensaje_texto.lower():
                hoy = str(date.today())
                if usuario.get("ultimo_reto_diario") == hoy:
                    responder_mensaje(numero_remitente, "Ya has completado tu reto diario de hoy. ¡Vuelve mañana por uno nuevo! Si quieres, puedes pedir un 'reto de práctica'.")
                else:
                    actualizar_usuario(numero_remitente, {"estado_conversacion": "eligiendo_tipo_reto", "es_diario": True}) # Marcador temporal
                    enviar_menu_tipo_reto(numero_remitente)
            elif '2' in mensaje_texto or 'práctica' in mensaje_texto.lower():
                actualizar_usuario(numero_remitente, {"estado_conversacion": "eligiendo_tipo_reto", "es_diario": False})
                enviar_menu_tipo_reto(numero_remitente)
            else:
                respuesta_chat = chat_conversacional_con_ia(mensaje_texto, estado, usuario.get("ultimo_mensaje_bot"))
                responder_mensaje(numero_remitente, respuesta_chat)

        elif estado == 'eligiendo_tipo_reto':
            tipo_reto = None
            if '1' in mensaje_texto or 'pseudo' in mensaje_texto.lower(): tipo_reto = 'Pseudocódigo'
            elif '2' in mensaje_texto or 'java' in mensaje_texto.lower(): tipo_reto = 'Java'
            elif '3' in mensaje_texto or 'python' in mensaje_texto.lower(): tipo_reto = 'Python'
            
            if tipo_reto:
                responder_mensaje(numero_remitente, f"¡Perfecto! Generando un reto de {tipo_reto} para tu nivel ({usuario['nivel']})...")
                reto = generar_reto_con_ia(usuario['nivel'], tipo_reto)
                if "error" in reto:
                    responder_mensaje(numero_remitente, reto["error"])
                    actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal"})
                    enviar_menu_principal(numero_remitente)
                else:
                    actualizaciones = {
                        "estado_conversacion": "resolviendo_reto",
                        "tipo_reto_actual": tipo_reto,
                        "reto_actual_titulo": reto["titulo"],
                        "reto_actual_enunciado": reto["enunciado"],
                        "reto_actual_solucion": reto["solucion_ideal"]
                    }
                    if usuario.get("es_diario"):
                        actualizaciones["ultimo_reto_diario"] = str(date.today())
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