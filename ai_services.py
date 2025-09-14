# ai_services.py

import os
import json
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def generar_reto_con_ia(nivel, tipo_reto, dificultad, tematica=None):
    if not GEMINI_API_KEY: return {"error": "IA no configurada."}
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres LogicBot, un tutor de programación divertido. Crea un reto de nivel {nivel}, dificultad **{dificultad}**, para **{tipo_reto}**. {f"El reto debe tratar sobre: '{tematica}'." if tematica else ""}
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
    if not GEMINI_API_KEY: return "❌ *INCORRECTO:* La evaluación no está configurada."
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    **Contexto:** Eres un tutor de programación que debe diferenciar entre una solución y una pregunta.
    **Problema a Resolver:** "{reto_enunciado}"
    **Mensaje del Estudiante:** "{solucion_usuario}"
    **Instrucciones:**
    1.  **Clasifica el Mensaje:** Primero, determina la intención del mensaje. ¿Es un intento de SOLUCIÓN o es una PREGUNTA sobre el tema?
    2.  **Si es una PREGUNTA:** Tu ÚNICA respuesta debe ser la palabra `[PREGUNTA]`. No respondas nada más.
    3.  **Si es una SOLUCIÓN:** Evalúa si el código en {tipo_reto} resuelve el problema. Si es correcta, empieza con "✅ *¡CORRECTO!*:". Si es incorrecta, empieza con "❌ *INCORRECTO:*:", seguido de una pista.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ *INCORRECTO:* Hubo un problema con mi cerebro de IA. Error: {e}"

def chat_conversacional_con_ia(mensaje_usuario, historial_chat, cursos_disponibles, tema_actual=None):
    if not GEMINI_API_KEY: return "Lo siento, el chat no está disponible."
    model = genai.GenerativeModel('gemini-1.5-flash')
    temas_python = ", ".join(cursos_disponibles['python']['lecciones'])
    prompt = f"""
    Eres "LogicBot", un tutor de programación amigable y conversacional.
    **Historial:** {historial_chat}
    **Mensaje del usuario:** "{mensaje_usuario}"
    **Cursos que ofreces:** Python Essentials (Temas: {temas_python}).
    {f"**Tema de la conversación actual:** Estás ayudando al usuario con un reto sobre '{tema_actual}'." if tema_actual else ""}

    **Reglas:**
    1.  **Sé Contextual:** Si se te da un 'Tema de la conversación actual', tu respuesta DEBE enfocarse en explicar o aclarar dudas sobre ese tema.
    2.  **Sé Útil:** Si el usuario pregunta qué temas enseñas, responde amablemente listando los temas y anímale a `empezar curso python`.
    3.  **Guía:** Si el usuario parece perdido y no hay un tema actual, recuérdale los comandos (`empezar curso python`, `reto python`).
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "No estoy seguro de cómo responder. Intenta con un comando como `empezar curso python`."

def explicar_tema_con_ia(tema):
    if not GEMINI_API_KEY: return "Lo siento, no puedo generar la explicación en este momento."
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres un profesor de programación excelente, capaz de explicar conceptos complejos de forma sencilla.
    **Tarea:** Explica el concepto de '{tema}' para un principiante.
    **Instrucciones:** Usa un lenguaje claro, analogías, un pequeño ejemplo de código en Python y emojis. Finaliza animando al estudiante.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"No pude generar la explicación. Error: {e}"