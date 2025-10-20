# ai_services.py

import os
import json
# --- IMPORTACIÓN CORRECTA PARA LA NUEVA LIBRERÍA ---
from google import genai
from config import CURSOS # Importamos los cursos

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- SINTAXIS CORRECTA: Inicializar el cliente ---
client = None
if GEMINI_API_KEY:
    # La configuración de la API key se maneja al crear el cliente
    client = genai.Client(api_key=GEMINI_API_KEY)

def generar_reto_con_ia(nivel, tipo_reto, dificultad, tematica=None):
    if not client: return {"error": "IA no configurada."}
    
    # --- MODELO Y SINTAXIS ACTUALIZADOS ---
    model = 'gemini-2.0-flash'
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
        response = client.models.generate_content(model=model, contents=prompt)
        # Accedemos al texto de la respuesta
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_text)
    except (json.JSONDecodeError, Exception) as e:
        return {"error": f"No pude generar el reto. Error de IA: {e}"}

def evaluar_solucion_con_ia(reto_enunciado, solucion_usuario, tipo_reto):
    if not client: return "❌ *INCORRECTO:* La evaluación no está configurada."
    
    # --- MODELO Y SINTAXIS ACTUALIZADOS ---
    model = 'gemini-2.0-flash'
    prompt = f"""
    **Contexto:** Eres un evaluador de código que debe diferenciar entre una solución y una pregunta.
    **Problema a Resolver:** "{reto_enunciado}"
    **Mensaje del Estudiante:** "{solucion_usuario}"
    **Instrucciones:**
    1.  **Clasifica:** ¿El mensaje contiene un bloque de código que intenta resolver el problema? Si es una pregunta clara como "¿cómo funciona un bucle?" o "¿puedes ayudarme?", responde ÚNICAMENTE con la palabra `[PREGUNTA]`.
    2.  **Evalúa:** Si el mensaje contiene lo que parece ser una solución en código {tipo_reto}, evalúala. Si es correcta, empieza con "✅ *¡CORRECTO!*:". Si es incorrecta, empieza con "❌ *INCORRECTO:*:", seguido de una pista conceptual (no código).
    """
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text
    except Exception as e:
        return f"❌ *INCORRECTO:* Hubo un problema con mi cerebro de IA. Error: {e}"

def chat_conversacional_con_ia(mensaje_usuario, historial_chat, tema_actual=None):
    if not client: return "Lo siento, el chat no está disponible."

    # --- MODELO Y SINTAXIS ACTUALIZADOS ---
    model = 'gemini-2.0-flash'
    prompt = f"""
    Eres "LogicBot", un tutor de programación amigable y conversacional. Tu objetivo es guiar al usuario para que resuelva los problemas por sí mismo, no darle la respuesta.
    **Historial:** {historial_chat}
    **Mensaje del usuario:** "{mensaje_usuario}"
    {f"**Tema de la conversación actual:** Estás ayudando al usuario con un reto sobre '{tema_actual}'." if tema_actual else ""}

    **REGLA DE ORO (MUY IMPORTANTE):**
    Bajo NINGUNA circunstancia escribas, completes o corrijas el código del usuario. No des soluciones directas. Tu rol es hacer preguntas y dar pistas conceptuales para que el usuario llegue a la solución por su cuenta.
    
    **Otras Reglas:**
    1.  **Si te piden ayuda:** Responde con una pregunta que le haga pensar.
    2.  **Si te piden la solución:** Niégate amablemente.
    3.  **Sé Contextual:** Si hay un 'Tema de la conversación actual', enfócate en ese tema.
    """
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text
    except Exception as e:
        return "No estoy seguro de cómo responder. Intenta con un comando como `menu`."

def explicar_tema_con_ia(tema):
    if not client: return "Lo siento, no puedo generar la explicación en este momento."
    
    # --- MODELO Y SINTAXIS ACTUALIZADOS ---
    model = 'gemini-2.0-flash'
    prompt = f"""
    Eres un profesor de programación excelente, capaz de explicar conceptos complejos de forma sencilla.
    **Tarea:** Explica el concepto de '{tema}' para un principiante.
    **Instrucciones:** Usa un lenguaje claro, analogías, un pequeño ejemplo de código y emojis. Finaliza animando al estudiante.
    """
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text
    except Exception as e:
        return f"No pude generar la explicación. Error: {e}"