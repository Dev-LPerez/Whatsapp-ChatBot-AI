# ai_services.py

import os
import json
from google import genai
from config import CURSOS

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


def generar_reto_con_ia(nivel, tipo_reto, dificultad, tematica=None):
    if not client: return {"error": "IA no configurada."}

    model = 'gemini-2.0-flash'
    prompt = f"""
    Eres LogicBot, un tutor de programación. Crea un reto de programación para un estudiante de nivel {nivel}.
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
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_text)
    except (json.JSONDecodeError, Exception) as e:
        return {"error": f"No pude generar el reto. Error de IA: {e}"}


def evaluar_solucion_con_ia(reto_enunciado, solucion_usuario, tipo_reto):
    if not client: return "❌ *INCORRECTO:* La evaluación no está configurada."

    model = 'gemini-2.0-flash'
    prompt = f"""
    **Contexto:** Eres un evaluador de código.
    **Problema:** "{reto_enunciado}"
    **Respuesta del Estudiante:** "{solucion_usuario}"
    **Instrucciones:**
    1. **Clasifica:** Si es una pregunta teórica ("qué es", "no entiendo"), responde solo `[PREGUNTA]`.
    2. **Evalúa:** Si es código/solución para {tipo_reto}:
       - Correcto: Empieza con "✅ *¡CORRECTO!*:".
       - Incorrecto: Empieza con "❌ *INCORRECTO:*:" y explica el error conceptualmente.
    """
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text
    except Exception as e:
        return f"❌ Error de IA: {e}"


def chat_conversacional_con_ia(mensaje_usuario, historial_chat, tema_actual=None):
    if not client: return "Lo siento, el chat no está disponible."

    model = 'gemini-2.0-flash'
    prompt = f"""
    Eres "LogicBot", un tutor de programación amigable.
    **Historial:** {historial_chat}
    **Mensaje del usuario:** "{mensaje_usuario}"

    **TUS DOS MODOS DE OPERACIÓN:**

    1. **MODO TEORÍA (El usuario pregunta "¿Qué es?", "¿Diferencia entre?", "No entiendo"):**
       - AQUÍ SÍ PUEDES EXPLICAR DIRECTAMENTE.
       - Usa analogías del mundo real (ej: cocina, videojuegos).
       - Sé claro y conciso.

    2. **MODO RETO/CÓDIGO (El usuario pide que le hagas el código o le des la solución a un ejercicio):**
       - AQUÍ NO DES LA SOLUCIÓN.
       - Usa el método socrático: haz preguntas guía.
       - Da pistas, no código completo.

    **Contexto actual:** {f"Estás en el tema '{tema_actual}'." if tema_actual else "Conversación general."}
    """
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text
    except Exception as e:
        return "No estoy seguro de cómo responder. Intenta con un comando como `menu`."


def explicar_tema_con_ia(tema):
    if not client: return "Lo siento, no puedo generar la explicación."

    model = 'gemini-2.0-flash'
    prompt = f"""
    Eres un profesor de programación.
    **Tarea:** Explica el concepto de '{tema}' para un principiante.
    **Instrucciones:** Usa lenguaje claro, analogías y un ejemplo de código.
    """
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"


def generar_introduccion_tema(tema):
    """Genera una mini-clase introductoria antes del reto."""
    if not client: return f"Vamos a aprender sobre {tema}."

    model = 'gemini-2.0-flash'
    prompt = f"""
    Actúa como un profesor experto de Java.
    El estudiante va a comenzar una lección sobre: "{tema}".

    **Tu objetivo:** Dar una "Mini-Clase" breve para que tenga las herramientas para resolver el reto que viene después.

    **Formato de respuesta (WhatsApp):**
    1. 🧠 **Concepto:** Definición en 1 frase sencilla.
    2. 💻 **Sintaxis:** Muestra cómo se escribe en código (breve snippet).
    3. 💡 **Tip Clave:** Un consejo rápido.

    No pongas ejercicios aquí, solo la enseñanza. Sé breve y animado.
    """
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text
    except Exception as e:
        return f"Comencemos con {tema}. ¡Prepárate!"


# --- ✅ NUEVA FUNCIÓN PARA COLECCIONABLES ---
def generar_cheat_sheet(tema):
    """Genera una ficha de resumen técnica y útil sobre un tema."""
    if not client: return f"Ficha de {tema} no disponible por el momento."

    model = 'gemini-2.0-flash'
    prompt = f"""
    Genera una "Cheat Sheet" (Hoja de Trucos) técnica y concisa sobre: {tema} en Java.
    Debe ser un recurso valioso que un programador quiera guardar.

    **Formato Estricto de WhatsApp:**
    📑 *CHEAT SHEET: {tema.upper()}*

    📌 *Sintaxis:*
    ```java
    // Código minimalista y claro aquí
    ```

    ⚡ *Cuándo usar:*
    [Explicación en 1 línea]

    ⚠️ *Errores comunes:*
    [1 punto clave a evitar]

    💡 *Pro-Tip:*
    [Un truco avanzado o buena práctica]

    Usa emojis técnicos. Sé directo. No saludes al principio ni te despidas al final. Solo entrega el contenido.
    """
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text
    except Exception as e:
        return f"No pude generar la ficha de colección. Error: {e}"