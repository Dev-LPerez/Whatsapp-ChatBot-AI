# ai_services.py

import os
import json
import google.generativeai as genai
from config import CURSOS # Importamos los cursos

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def generar_reto_con_ia(nivel, tipo_reto, dificultad, tematica=None):
    if not GEMINI_API_KEY: return {"error": "IA no configurada."}
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres LogicBot, un tutor de programación divertido. Crea un reto de programación para un estudiante de nivel {nivel}.
    - **Lenguaje/Tema:** {tipo_reto}
    - **Dificultad:** {dificultad}
    {f"- **Temática Específica:** '{tematica}'." if tematica else ""}
    
    Tu respuesta DEBE ser un objeto JSON válido con "enunciado", "solucion_ideal" y "pistas".
    - "enunciado": El texto del reto, claro, conciso y con emojis 💡.
    - "solucion_ideal": La solución ejemplar en el lenguaje especificado.
    - "pistas": Un array de 3 strings con pistas conceptuales progresivas.
    """
    try:
        response = model.generate_content(prompt)
        # Limpieza robusta del JSON
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_text)
    except (json.JSONDecodeError, Exception) as e:
        return {"error": f"No pude generar el reto. Error de IA: {e}"}

def evaluar_solucion_con_ia(reto_enunciado, solucion_usuario, tipo_reto):
    # (El prompt actual es muy bueno y cumple RF-14, se mantiene)
    if not GEMINI_API_KEY: return "❌ *INCORRECTO:* La evaluación no está configurada."
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    **Contexto:** Eres un evaluador de código que debe diferenciar entre una solución y una pregunta.
    **Problema a Resolver:** "{reto_enunciado}"
    **Mensaje del Estudiante:** "{solucion_usuario}"
    **Instrucciones:**
    1.  **Clasifica:** ¿El mensaje contiene un bloque de código que intenta resolver el problema? Si es una pregunta clara como "¿cómo funciona un bucle?" o "¿puedes ayudarme?", responde ÚNICAMENTE con la palabra `[PREGUNTA]`.
    2.  **Evalúa:** Si el mensaje contiene lo que parece ser una solución en código {tipo_reto}, evalúala. Si es correcta, empieza con "✅ *¡CORRECTO!*:". Si es incorrecta, empieza con "❌ *INCORRECTO:*:", seguido de una pista conceptual (no código).
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ *INCORRECTO:* Hubo un problema con mi cerebro de IA. Error: {e}"

def chat_conversacional_con_ia(mensaje_usuario, historial_chat, tema_actual=None):
    # (El prompt actual cumple RF-12 y RF-16, se mantiene)
    if not GEMINI_API_KEY: return "Lo siento, el chat no está disponible."
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres "LogicBot", un tutor de programación amigable y conversacional. Tu objetivo es guiar al usuario para que resuelva los problemas por sí mismo, no darle la respuesta.
    **Historial:** {historial_chat}
    **Mensaje del usuario:** "{mensaje_usuario}"
    {f"**Tema de la conversación actual:** Estás ayudando al usuario con un reto sobre '{tema_actual}'." if tema_actual else ""}

    **REGLA DE ORO (MUY IMPORTANTE):**
    Bajo NINGUNA circunstancia escribas, completes o corrijas el código del usuario. No des soluciones directas. Tu rol es hacer preguntas y dar pistas conceptuales para que el usuario llegue a la solución por su cuenta.
    
    **Otras Reglas:**
    1.  **Si te piden ayuda:** Responde con una pregunta que le haga pensar. Ejemplo: "¿Qué crees que debería ir dentro de ese bucle para que se detenga?".
    2.  **Si te piden la solución:** Niégate amablemente. Ejemplo: "¡El objetivo es que lo descubras tú! Sigue intentándolo. Si te sientes muy atascado, siempre puedes escribir `me rindo`."
    3.  **Sé Contextual:** Si hay un 'Tema de la conversación actual', enfócate en ese tema.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "No estoy seguro de cómo responder. Intenta con un comando como `menu`."

def explicar_tema_con_ia(tema):
    # (Sin cambios, cumple su función perfectamente)
    if not GEMINI_API_KEY: return "Lo siento, no puedo generar la explicación en este momento."
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres un profesor de programación excelente, capaz de explicar conceptos complejos de forma sencilla.
    **Tarea:** Explica el concepto de '{tema}' para un principiante.
    **Instrucciones:** Usa un lenguaje claro, analogías, un pequeño ejemplo de código y emojis. Finaliza animando al estudiante.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"No pude generar la explicación. Error: {e}"