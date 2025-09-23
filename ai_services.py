# ai_services.py

import os
import json
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def generar_reto_con_ia(nivel, tipo_reto, dificultad, tematica=None):
    # Esta función no cambia
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
    # PROMPT MEJORADO: Más estricto para detectar soluciones
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

def chat_conversacional_con_ia(mensaje_usuario, historial_chat, cursos_disponibles, tema_actual=None):
    # PROMPT MEJORADO: Con reglas estrictas para no dar la solución
    if not GEMINI_API_KEY: return "Lo siento, el chat no está disponible."
    model = genai.GenerativeModel('gemini-1.5-flash')
    temas_python = ", ".join(cursos_disponibles['python']['lecciones'])
    prompt = f"""
    Eres "LogicBot", un tutor de programación. Tu objetivo es guiar al usuario para que resuelva los problemas por sí mismo, no darle la respuesta.
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
    # Esta función no cambia
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