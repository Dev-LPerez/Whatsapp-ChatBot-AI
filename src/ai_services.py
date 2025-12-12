# ai_services.py

import os
import json
from google import genai
from src.config.config import CURSOS

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


def generar_reto_con_ia(nivel, tipo_reto, dificultad, tematica=None):
    """
    Genera un reto de programación validado por IA.
    Incluye un campo 'tiempo_estimado' oculto para detectar copy-paste.
    """
    if not client: return {"error": "IA no configurada."}

    model = 'gemini-2.0-flash'
    prompt = f"""
    Eres LogicBot, un tutor de programación. Crea un reto de programación para un estudiante de nivel {nivel}.
    - **Lenguaje/Tema:** {tipo_reto}
    - **Dificultad:** {dificultad}
    {f"- **Temática Específica:** '{tematica}'." if tematica else ""}

    Tu respuesta DEBE ser un objeto JSON válido con la siguiente estructura exacta:
    {{
        "enunciado": "Texto del reto, claro, conciso y con emojis 💡.",
        "solucion_ideal": "La solución ejemplar en código.",
        "pistas": ["Pista 1", "Pista 2", "Pista 3"],
        "tiempo_estimado": 120  // Número ENTERO: Segundos estimados que tomaría a un humano promedio escribir esto (sé generoso).
    }}
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
    Eres "LogicBot", un tutor de programación experto EXCLUSIVAMENTE en **JAVA**.
    **Historial:** {historial_chat}
    **Mensaje del usuario:** "{mensaje_usuario}"

    🛑 **REGLA DE ORO (CONTEXTO):**
    Tu especialidad es JAVA. Si el usuario te pregunta sobre:
    - Otros lenguajes (Python, C++, JS, etc.) -> Rechaza amablemente y ofrece la alternativa en Java.
    - Temas no técnicos (Cocina, deportes, etc.) -> Recuerda que eres un bot educativo.

    *Ejemplo de rechazo:* "🤖 Interesante pregunta, pero mi especialidad es Java. En Java, ese concepto se maneja así..."

    **TUS DOS MODOS DE OPERACIÓN (SOLO PARA JAVA):**

    1. **MODO TEORÍA (El usuario pregunta "¿Qué es?", "¿Diferencia entre?", "No entiendo"):**
       - Explica el concepto en el contexto de Java.
       - Usa analogías del mundo real (ej: cocina, videojuegos).
       - Sé claro y conciso.

    2. **MODO RETO/CÓDIGO (El usuario pide que le hagas el código o le des la solución):**
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


# --- ✅ NUEVAS FUNCIONES FASE 3 (ANTI-PLAGIO Y DEPURACIÓN) ---

def generar_reto_depuracion(nivel, tematica):
    """Genera un código que PARECE correcto pero tiene un bug lógico o de sintaxis."""
    if not client: return {"error": "IA no configurada"}

    model = 'gemini-2.0-flash'
    prompt = f"""
    Genera un 'Reto de Depuración' (Debugging) para Java, Nivel {nivel}, tema '{tematica}'.

    1. Crea un código breve que tenga UN (1) error sutil (lógico o de sintaxis común).
    2. El error no debe ser obvio a simple vista.

    Salida JSON:
    {{
        "enunciado": "Encuentra el error en este código: ... (código con bug aquí)",
        "solucion_ideal": "El error está en la línea X. La corrección es...",
        "pistas": ["Revisa los tipos de datos", "Mira bien el bucle", "Chequea la condición"],
        "bug_explicacion": "Explicación breve del error para el profesor",
        "tiempo_estimado": 60 
    }}
    """
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_text)
    except Exception as e:
        return {"error": f"Error generando debug: {e}"}


def generar_pregunta_defensa(enunciado, solucion_usuario):
    """Genera una pregunta socrática para validar comprensión."""
    if not client: return "Explícame tu código paso a paso."

    model = 'gemini-2.0-flash'
    prompt = f"""
    El estudiante ha resuelto este reto correctamente.
    Reto: {enunciado}
    Solución del estudiante: {solucion_usuario}

    Genera UNA sola pregunta corta y directa para verificar que NO copió el código.
    Pregunta sobre el "por qué" de una decisión específica (ej: por qué ese tipo de bucle, por qué esa variable).
    No felicites, ve directo a la pregunta.
    """
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text
    except Exception as e:
        return "¿Podrías explicarme la lógica de tu solución?"


def evaluar_defensa(pregunta, respuesta_usuario, contexto_reto):
    """Evalúa si la justificación del estudiante tiene sentido."""
    if not client: return True  # Fallback

    model = 'gemini-2.0-flash'
    prompt = f"""
    Contexto: {contexto_reto}
    Pregunta de control: {pregunta}
    Respuesta del estudiante: {respuesta_usuario}

    ¿La respuesta demuestra que el estudiante entiende su propio código?
    Responde SOLO "SI" o "NO".
    """
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        text = response.text.strip().upper()
        return "SI" in text
    except Exception:
        return True