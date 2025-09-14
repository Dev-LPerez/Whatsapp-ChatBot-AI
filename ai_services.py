# ai_services.py

import os
import json
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def generar_reto_con_ia(nivel, tipo_reto, dificultad, tematica=None):
    """Genera un reto de programación usando la IA de Gemini."""
    if not GEMINI_API_KEY: return {"error": "IA no configurada."}
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres LogicBot, un tutor de programación divertido.
    Crea un reto de nivel {nivel}, dificultad **{dificultad}**, para **{tipo_reto}**.
    {f"El reto debe tratar sobre: '{tematica}'." if tematica else ""}
    
    Tu respuesta DEBE ser un objeto JSON válido con "enunciado", "solucion_ideal" y "pistas".
    - "enunciado": El texto del reto, con título en negrita y emojis 💡.
    - "solucion_ideal": La solución ejemplar.
    - "pistas": Un array de 3 strings con pistas progresivas.
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.strip().replace("```json", "").replace("```", ""))
    except Exception as e:
        return {"error": f"No pude generar el reto. Error de IA: {e}"}

def evaluar_solucion_con_ia(reto_enunciado, solucion_usuario, tipo_reto):
    """Evalúa la solución de un usuario con la IA de Gemini."""
    if not GEMINI_API_KEY: return "❌ *INCORRECTO:* La evaluación no está configurada."
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    **Contexto:** Eres un tutor de programación estricto y preciso.
    **Tarea:** Evaluar si la solución de un estudiante resuelve el problema planteado.
    **Problema a Resolver:** "{reto_enunciado}"
    **Solución del Estudiante en {tipo_reto}:** "{solucion_usuario}"
    **Instrucciones de Evaluación:**
    1.  **Compara Estrictamente:** Tu única tarea es determinar si la solución resuelve el **Problema a Resolver**. Si resuelve un problema diferente, tu respuesta DEBE ser "INCORRECTO".
    2.  **Formato Obligatorio:** Si es correcta, empieza con "✅ *¡CORRECTO!*:". Si es incorrecta, empieza con "❌ *INCORRECTO:*:", seguido de una pista clara.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ *INCORRECTO:* Hubo un problema con mi cerebro de IA. ¿Podrías intentar de nuevo? Error: {e}"

def chat_conversacional_con_ia(mensaje_usuario, historial_chat, reto_actual_solucion=None):
    """Maneja una conversación general con el usuario usando la IA de Gemini."""
    if not GEMINI_API_KEY: return "Lo siento, el chat no está disponible."
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres "LogicBot", un tutor de programación amigable que usa emojis.
    **Historial de Conversación (últimos 4 mensajes):** {historial_chat}
    **Mensaje del usuario:** "{mensaje_usuario}"
    **Reglas:**
    1.  **Sé Contextual:** Responde basándote en el historial.
    2.  **Guía al Usuario:** Explica comandos (`reto python`, `mi perfil`, `pista`, etc.).
    3.  **Si se Rinde (CRÍTICO):** Si el usuario dice `me rindo` y tienes una solución (`{reto_actual_solucion}`), TU ÚNICA ACCIÓN es dar la solución con una explicación detallada de cómo funciona, sin hacer más preguntas.
    4.  **Mantente Enfocado:** Rechaza amablemente temas no relacionados con programación.
    **Tu respuesta:**
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "No estoy seguro de cómo responder. Intenta con un comando como `reto python`."