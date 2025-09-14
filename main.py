# main.py (Versión 2.0 - Amigable y Explicativa)

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

# --- FUNCIONES DE IA (PROMPTS MEJORADOS) ---

def generar_reto_con_ia(nivel, tipo_reto):
    if not GEMINI_API_KEY: return {"error": "IA no configurada."}
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres LogicBot, un tutor de programación divertido y creativo.
    Genera un reto de programación de nivel {nivel} para **{tipo_reto}**.
    Tu respuesta DEBE ser un objeto JSON válido con "enunciado" y "solucion_ideal".
    - "enunciado": El texto del reto. Usa emojis 💡, un título en negrita y formato claro. Pide la solución en {tipo_reto}.
    - "solucion_ideal": La solución ejemplar en {tipo_reto}, bien comentada.
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.strip().replace("```json", "").replace("```", ""))
    except Exception as e:
        print(f"Error al generar reto con IA: {e}")
        return {"error": "Ups... 🤖 Tuve un problema para generar un reto. ¿Intentamos de nuevo?"}

def evaluar_solucion_con_ia(reto_enunciado, solucion_usuario, tipo_reto):
    if not GEMINI_API_KEY: return "INCORRECTO: La evaluación no está configurada."
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    **Contexto:** Eres un tutor de programación estricto pero justo.
    **Tarea:** Evaluar la solución de un estudiante.
    **Problema a Resolver:** "{reto_enunciado}"
    **Solución del Estudiante ({tipo_reto}):** "{solucion_usuario}"
    **Instrucciones:**
    1.  Si la solución es correcta, empieza con "✅ *¡CORRECTO!*:" y da un feedback positivo y breve.
    2.  Si la solución es incorrecta o no tiene que ver con el problema, empieza con "❌ *INCORRECTO:*:" y da una pista clara y constructiva.
    3.  Usa emojis para hacer el feedback más amigable.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ *INCORRECTO:* Hubo un problema con mi cerebro de IA... 🧠💥. ¿Podrías intentar enviar tu solución de nuevo? Error: {e}"

def chat_conversacional_con_ia(mensaje_usuario, reto_actual_solucion=None):
    if not GEMINI_API_KEY: return "Lo siento, el chat no está disponible."
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres "LogicBot", un tutor de programación amigable, paciente y que usa emojis.
    **Comandos Principales:** `reto python`, `reto java`, `reto pseudocodigo`, `solucion: [tu respuesta]`, `me rindo`.
    
    **Reglas de Comportamiento:**
    1.  **Guía al Usuario:** Si parece perdido, recuérdale los comandos de forma amigable. Si pregunta cómo responder, explícale que debe usar `*solucion:*` seguido de su código.
    2.  **Ayuda con Dudas:** Responde cualquier pregunta sobre programación de forma sencilla y con ejemplos si es necesario.
    3.  **Si se Rinde (Instrucción CRÍTICA):** Si el usuario dice "me rindo", "no sé", o pide la solución, y tienes una solución (`{reto_actual_solucion}`), tu respuesta DEBE tener dos partes:
        - **La Solución:** Presenta el código de la solución formateado con ``` para que se vea como un bloque.
        - **La Explicación:** Después del código, añade un apartado llamado "*🔍 ¿Cómo funciona este código?*" y explica la solución paso a paso de forma clara. Usa emojis para ilustrar.
    4.  **Mantente Enfocado:** Si te preguntan algo no relacionado con programación, rechaza amablemente y redirige la conversación. Ejemplo: "¡Esa es una buena pregunta! Pero mi procesador está 100% dedicado a la programación 🤖. ¿Te gustaría intentar un reto?"

    **Mensaje del usuario:** "{mensaje_usuario}"
    **Tu respuesta:**
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "🤔 No estoy seguro de cómo responder a eso. Recuerda que puedes pedirme un reto con `reto python`, por ejemplo."

# --- FUNCIÓN PARA ENVIAR MENSAJES ---
def responder_mensaje(numero_destinatario, texto_respuesta):
    if not WHATSAPP_TOKEN or not ID_NUMERO_TELEFONO:
        return
    url = f"[https://graph.facebook.com/v19.0/](https://graph.facebook.com/v19.0/){ID_NUMERO_TELEFONO}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    # Usamos "text" con "preview_url" en False para mejor formato de links si los hubiera
    data = {"messaging_product": "whatsapp", "to": numero_destinatario, "text": {"preview_url": False, "body": texto_respuesta}}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar mensaje: {e}")

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

        usuario = obtener_usuario(numero_remitente)

        if not usuario:
            crear_usuario(numero_remitente, nombre_usuario)
            bienvenida = (
                f"¡Hola, {nombre_usuario}! 👋 Soy LogicBot, tu tutor de programación personal.\n\n"
                "¡Estoy aquí para ayudarte a pensar como un programador! 🚀\n\n"
                "Puedes pedirme un reto cuando quieras con uno de estos comandos:\n"
                "➡️ `reto python`\n"
                "➡️ `reto java`\n"
                "➡️ `reto pseudocodigo`"
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
                responder_mensaje(numero_remitente, f"¡Claro! 👨‍💻 Buscando un reto de *{tipo_reto}* para tu Nivel {usuario['nivel']}...")
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
                responder_mensaje(numero_remitente, "🤔 No especificaste un lenguaje. Prueba con `reto python`, `reto java` o `reto pseudocodigo`.")

        elif mensaje_lower.startswith("solucion:"):
            if not usuario.get("reto_actual_enunciado"):
                responder_mensaje(numero_remitente, "¡Ups! 😅 No tienes un reto activo para resolver. ¡Pide uno nuevo!")
            else:
                solucion_usuario = mensaje_texto[len("solucion:"):].strip()
                feedback = evaluar_solucion_con_ia(usuario["reto_actual_enunciado"], solucion_usuario, usuario["reto_actual_tipo"])
                responder_mensaje(numero_remitente, feedback)
                if feedback.strip().upper().startswith("✅"):
                    nuevo_nivel = usuario["nivel"] + 1
                    actualizar_usuario(numero_remitente, {"nivel": nuevo_nivel, "reto_actual_enunciado": None, "reto_actual_solucion": None, "reto_actual_tipo": None})
                    responder_mensaje(numero_remitente, f"🚀 ¡Felicidades! Has subido al Nivel {nuevo_nivel}. Pide tu próximo reto cuando estés listo.")

        elif mensaje_lower == "me rindo":
             if not usuario.get("reto_actual_solucion"):
                responder_mensaje(numero_remitente, "Tranquilo, no tienes ningún reto activo para rendirte. ¡Pide uno cuando quieras! 👍")
             else:
                respuesta_con_explicacion = chat_conversacional_con_ia("me rindo", usuario.get("reto_actual_solucion"))
                actualizar_usuario(numero_remitente, {"reto_actual_enunciado": None, "reto_actual_solucion": None, "reto_actual_tipo": None})
                responder_mensaje(numero_remitente, respuesta_con_explicacion)
        
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