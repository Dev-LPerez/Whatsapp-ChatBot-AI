# main.py

import json
import requests
import sqlite3
import google.generativeai as genai
from fastapi import FastAPI, Request, Response

app = FastAPI()

# --- IMPORTANTE: CONFIGURACIÓN ---
WHATSAPP_TOKEN = "EAATGDUciZACABPfb6PzXTedNr53cTioUjfrZCyTl27kDHkVkd7GhjnjJnjh7CwXv0e2528EgjthaMWoJTgz9fLp52lZCPUHLB1s1xmm5TDZBQXZA0HLuOaZBUq6qLM6uA8ZCgdSxXD6qI6wAutpo8QfSGaDBp2EL3yE6t1treEDVJRiWW0uB10RKe3N6jO8OBbBAi37reKhqPzS2AaHumbLV2E8qD09bZCRAevEtBpucqRcZD"
ID_NUMERO_TELEFONO = "843900795475100"
GEMINI_API_KEY = "AIzaSyAtSPegfvfpGNG1BInkGZ7fWJtTRVJoMlM"

genai.configure(api_key=GEMINI_API_KEY)

# --- NUEVO: CONFIGURACIÓN DE LA BASE DE DATOS ---
DB_NAME = "database.db"

def inicializar_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Creamos la tabla 'usuarios' si no existe
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        numero_telefono TEXT PRIMARY KEY,
        nombre TEXT,
        nivel INTEGER
    )
    """)
    conn.commit()
    conn.close()

# --- BANCO DE RETOS (sin cambios) ---
banco_de_retos = {
    1: {
        "id": "L1-001",
        "titulo": "Sumar dos números.",
        "enunciado": (
            "¡Aquí va tu primer reto de lógica! 🧠\n\n"
            "**Reto #1: Sumar dos números.**\n"
            "Describe en pseudocódigo los pasos para pedirle al usuario dos números, sumarlos y mostrar el resultado.\n\n"
            "Para enviar tu respuesta, escribe `solucion:` seguido de tu pseudocódigo."
        ),
        "solucion_ideal": "INICIO, PEDIR numero1, PEDIR numero2, resultado = numero1 + numero2, MOSTRAR resultado, FIN"
    },
    2: {
        "id": "L2-001",
        "titulo": "Número Par o Impar.",
        "enunciado": (
            "¡Subamos de nivel! 💪\n\n"
            "**Reto #2: Número Par o Impar.**\n"
            "Describe en pseudocódigo la lógica para determinar si un número es par o impar.\n\n"
            "Para enviar tu respuesta, escribe `solucion:` seguido de tu pseudocódigo."
        ),
        "solucion_ideal": "INICIO, PEDIR numero, SI (numero % 2 == 0) ENTONCES MOSTRAR 'Par' SINO MOSTRAR 'Impar', FIN"
    }
}

# --- NUEVO: FUNCIONES PARA INTERACTUAR CON LA DB ---
def obtener_usuario(numero_telefono):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, nivel FROM usuarios WHERE numero_telefono = ?", (numero_telefono,))
    usuario = cursor.fetchone() # fetchone() devuelve una tupla (nombre, nivel) o None
    conn.close()
    if usuario:
        # Devolvemos un diccionario para que sea fácil de usar
        return {"nombre": usuario[0], "nivel": usuario[1]}
    return None

def crear_usuario(numero_telefono, nombre):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Todos los usuarios nuevos empiezan en el nivel 1
    cursor.execute("INSERT INTO usuarios (numero_telefono, nombre, nivel) VALUES (?, ?, ?)", (numero_telefono, nombre, 1))
    conn.commit()
    conn.close()

def actualizar_nivel_usuario(numero_telefono, nuevo_nivel):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET nivel = ? WHERE numero_telefono = ?", (nuevo_nivel, numero_telefono))
    conn.commit()
    conn.close()


# --- WEBHOOK (actualizado para usar la DB) ---
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

            # Buscamos al usuario en la base de datos
            usuario_actual = obtener_usuario(numero_remitente)

            if not usuario_actual:
                crear_usuario(numero_remitente, nombre_usuario)
                texto_respuesta = f"¡Hola, {nombre_usuario}! 👋 Te he registrado en el bot de retos. Escribe 'reto' para empezar."
                responder_mensaje(numero_remitente, texto_respuesta)
                return Response(status_code=200)

            # Lógica de comandos
            nivel_actual = usuario_actual["nivel"]
            mensaje_lower = mensaje_texto.lower()

            if mensaje_texto.lower().startswith("solucion:"):
                solucion_usuario = mensaje_texto[len("solucion:"):].strip()
                reto_actual_enunciado = banco_de_retos[nivel_actual]["enunciado"]
                
                feedback_ia = evaluar_solucion_con_ia(reto_actual_enunciado, solucion_usuario)
                responder_mensaje(numero_remitente, feedback_ia)

                if feedback_ia.strip().upper().startswith("CORRECTO"):
                    nuevo_nivel = nivel_actual + 1
                    actualizar_nivel_usuario(numero_remitente, nuevo_nivel)
                    agradecimiento = f"\n\n¡Felicidades! Has avanzado al nivel {nuevo_nivel}. Escribe 'reto' para tu nuevo desafío."
                    responder_mensaje(numero_remitente, agradecimiento)

            elif "reto" in mensaje_lower:
                if nivel_actual in banco_de_retos:
                    texto_respuesta = banco_de_retos[nivel_actual]["enunciado"]
                    responder_mensaje(numero_remitente, texto_respuesta)
                else:
                    responder_mensaje(numero_remitente, "¡Felicidades! Has completado todos los retos. 🎉")
            else:
                texto_respuesta = "Comando no reconocido. Escribe 'reto' o envía tu respuesta con `solucion: ...`."
                responder_mensaje(numero_remitente, texto_respuesta)

    except Exception as e:
        print(f"Ocurrió un error no manejado: {e}")
        pass

    return Response(status_code=200)


# --- Se ejecuta una sola vez al iniciar el servidor ---
@app.on_event("startup")
async def startup_event():
    inicializar_db()

# --- El resto del código (evaluar_solucion_con_ia, responder_mensaje, verificar_webhook) se queda igual ---

def evaluar_solucion_con_ia(reto_enunciado, solucion_usuario):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres un tutor de programación experto y amigable. Tu tarea es evaluar la solución de pseudocódigo de un estudiante.
    - **Tarea del estudiante:** "{reto_enunciado}"
    - **Solución del estudiante:** "{solucion_usuario}"

    Evalúa la solución del estudiante. Responde en español y de forma concisa.
    Tu respuesta DEBE empezar con "CORRECTO:" si la lógica es correcta, o "INCORRECTO:" si la lógica es incorrecta.
    Después, en no más de dos frases, dale un feedback útil y amigable.
    Si es incorrecto, dale una pista clave, pero no la solución completa.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error al llamar a la API de Gemini: {e}")
        return "INCORRECTO: Hubo un problema al contactar al tutor de IA. Intenta de nuevo."

def responder_mensaje(numero_destinatario, texto_respuesta):
    url = f"https://graph.facebook.com/v19.0/{ID_NUMERO_TELEFONO}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": numero_destinatario, "text": {"body": texto_respuesta}}
    response = requests.post(url, headers=headers, json=data)
    print(f"Respuesta de la API de Meta: {response.status_code}")
    print(response.json())

@app.get("/webhook")
async def verificar_webhook(request: Request):
    VERIFY_TOKEN = "micodigosecreto"
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode and token and mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, status_code=200)
    return Response(status_code=403)