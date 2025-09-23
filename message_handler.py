# message_handler.py

import json
import database as db
import ai_services as ai
from config import CURSOS, UMBRAL_DE_FALLOS, PUNTOS_POR_DIFICULTAD, PUNTOS_PARA_NIVEL_UP
from whatsapp_utils import responder_mensaje, enviar_menu_interactivo, enviar_botones_basicos

# --- MANEJADORES DE MENSAJES INTERACTIVOS (BOTONES/MENÚS) ---

def handle_interactive_message(id_seleccion, numero_remitente, usuario):
    historial_chat = json.loads(usuario.get("historial_chat", "[]"))

    if id_seleccion == 'mostrar_menu':
        enviar_menu_interactivo(numero_remitente)
    elif id_seleccion.startswith("iniciar_curso_"):
        curso_key = id_seleccion.split("_")[-1]
        iniciar_curso(numero_remitente, usuario, curso_key)
    elif id_seleccion == "pedir_reto_aleatorio":
        db.actualizar_usuario(numero_remitente, {"estado_conversacion": "eligiendo_lenguaje_reto"})
        botones = [
            {"id": "elegir_reto_python", "title": "Python 🐍"},
            {"id": "elegir_reto_java", "title": "Java ☕"},
            {"id": "elegir_reto_pseudocodigo", "title": "Pseudocódigo 🧠"}
        ]
        enviar_botones_basicos(numero_remitente, "¿De qué lenguaje quieres el reto?", botones)
    elif id_seleccion.startswith("elegir_reto_"):
        tipo_reto = id_seleccion.split("_")[-1]
        db.actualizar_usuario(numero_remitente, {"estado_conversacion": "eligiendo_dificultad", "tipo_reto_actual": tipo_reto})
        responder_mensaje(numero_remitente, "¿Qué nivel de dificultad prefieres? 🤔\n\n1. Fácil 🌱\n2. Intermedio 🔥\n3. Difícil 🤯", historial_chat)
    elif id_seleccion == "ver_mi_perfil":
        mostrar_perfil(numero_remitente, usuario, historial_chat)

# --- MANEJADORES DE MENSAJES DE TEXTO POR ESTADO ---

def handle_text_message(mensaje_texto, numero_remitente, usuario):
    historial_chat = json.loads(usuario.get("historial_chat", "[]"))
    historial_chat.append({"usuario": mensaje_texto})
    estado = usuario.get("estado_conversacion", "menu_principal")
    mensaje_lower = mensaje_texto.lower()

    # 1. Comandos Globales
    if mensaje_lower == "menu":
        enviar_menu_interactivo(numero_remitente)
        return
    if mensaje_lower == "me rindo":
        rendirse(numero_remitente, usuario, historial_chat)
        return
    if mensaje_lower == "mi perfil":
        mostrar_perfil(numero_remitente, usuario, historial_chat)
        return

    # 2. Lógica por Estado Conversacional
    if estado == "eligiendo_dificultad":
        handle_seleccion_dificultad(mensaje_texto, numero_remitente, usuario, historial_chat)
    elif estado in ["en_curso", "resolviendo_reto"]:
        handle_solucion_reto(mensaje_texto, numero_remitente, usuario, historial_chat)
    elif estado == "esperando_ayuda_teorica":
        handle_ayuda_teorica(mensaje_texto, numero_remitente, usuario, historial_chat)
    else: # menu_principal o cualquier otro estado
        respuesta_chat = ai.chat_conversacional_con_ia(mensaje_texto, historial_chat)
        responder_mensaje(numero_remitente, respuesta_chat, historial_chat)

# --- LÓGICA DE ACCIONES ESPECÍFICAS ---

def iniciar_curso(numero_remitente, usuario, curso_key):
    if curso_key not in CURSOS:
        responder_mensaje(numero_remitente, "Lo siento, ese curso no está disponible.", [])
        return
    
    curso = CURSOS[curso_key]
    leccion_actual = 0
    db.actualizar_usuario(numero_remitente, {
        "estado_conversacion": "en_curso",
        "curso_actual": curso_key,
        "leccion_actual": leccion_actual,
        "intentos_fallidos": 0
    })
    
    mensaje_inicio = f"¡Excelente! 🎉 Iniciaste la ruta de aprendizaje: *{curso['nombre']}*.\n\nTu primera lección: **{curso['lecciones'][leccion_actual]}**.\n\nGenerando tu primer reto..."
    historial_chat = json.loads(usuario.get("historial_chat", "[]"))
    responder_mensaje(numero_remitente, mensaje_inicio, historial_chat)
    
    generar_y_enviar_reto(numero_remitente, usuario, curso_key, "Fácil", curso['lecciones'][leccion_actual])

def handle_seleccion_dificultad(mensaje_texto, numero_remitente, usuario, historial_chat):
    dificultad = None
    mensaje_lower = mensaje_texto.lower()
    if "1" in mensaje_texto or "fácil" in mensaje_lower: dificultad = "Fácil"
    elif "2" in mensaje_texto or "intermedio" in mensaje_lower: dificultad = "Intermedio"
    elif "3" in mensaje_texto or "difícil" in mensaje_lower: dificultad = "Difícil"
    
    if dificultad:
        tipo_reto = usuario["tipo_reto_actual"]
        responder_mensaje(numero_remitente, f"¡Entendido! 👨‍💻 Buscando un reto de *{tipo_reto}* con dificultad *{dificultad}*...", historial_chat)
        generar_y_enviar_reto(numero_remitente, usuario, tipo_reto, dificultad)
    else:
        respuesta_chat = ai.chat_conversacional_con_ia(mensaje_texto, historial_chat, "elección de dificultad")
        responder_mensaje(numero_remitente, respuesta_chat, historial_chat)

def handle_solucion_reto(mensaje_texto, numero_remitente, usuario, historial_chat):
    tipo_reto = usuario.get("curso_actual") or usuario.get("tipo_reto_actual")
    feedback = ai.evaluar_solucion_con_ia(usuario["reto_actual_enunciado"], mensaje_texto, tipo_reto)
    
    if "[PREGUNTA]" in feedback:
        tema_actual = "programación en general"
        if usuario.get("curso_actual"):
            tema_actual = CURSOS[usuario["curso_actual"]]["lecciones"][usuario["leccion_actual"]]
        respuesta_conversacional = ai.chat_conversacional_con_ia(mensaje_texto, historial_chat, tema_actual)
        responder_mensaje(numero_remitente, respuesta_conversacional, historial_chat)
    
    elif feedback.strip().upper().startswith("✅"):
        # Lógica de acierto
        responder_mensaje(numero_remitente, feedback, historial_chat)
        procesar_acierto(numero_remitente, usuario, historial_chat)
    else:
        # Lógica de fallo
        responder_mensaje(numero_remitente, feedback, historial_chat)
        procesar_fallo(numero_remitente, usuario, historial_chat)
        
def procesar_acierto(numero_remitente, usuario, historial_chat):
    # Otorgar puntos
    dificultad = usuario.get("dificultad_reto_actual", "Fácil")
    puntos_ganados = PUNTOS_POR_DIFICULTAD.get(dificultad, 5)
    racha = usuario.get("racha_dias", 1)
    puntos_con_bonus = puntos_ganados + racha
    puntos_actuales = usuario.get("puntos", 0) + puntos_con_bonus
    
    mensaje_puntos = f"¡Ganaste *{puntos_ganados}* puntos + *{racha}* de bonus por tu racha! Total: *{puntos_con_bonus}* puntos. ✨"
    responder_mensaje(numero_remitente, mensaje_puntos, historial_chat)

    # Subir de nivel
    if puntos_actuales >= PUNTOS_PARA_NIVEL_UP * usuario.get("nivel", 1):
        nuevo_nivel = usuario.get("nivel", 1) + 1
        db.actualizar_usuario(numero_remitente, {"nivel": nuevo_nivel})
        responder_mensaje(numero_remitente, f"¡Felicidades! 🥳 ¡Has subido al **Nivel {nuevo_nivel}**! Sigue así.", historial_chat)
    
    db.actualizar_usuario(numero_remitente, {"puntos": puntos_actuales})

    # Avanzar en el curso o finalizar reto
    if usuario.get("estado_conversacion") == "en_curso":
        avanzar_leccion(numero_remitente, usuario, historial_chat)
    else:
        db.actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal", "reto_actual_enunciado": None, "reto_actual_solucion": None})
        enviar_menu_interactivo(numero_remitente)

def avanzar_leccion(numero_remitente, usuario, historial_chat):
    curso_key = usuario["curso_actual"]
    curso = CURSOS[curso_key]
    nueva_leccion = usuario["leccion_actual"] + 1

    if nueva_leccion < len(curso["lecciones"]):
        db.actualizar_usuario(numero_remitente, {"leccion_actual": nueva_leccion, "intentos_fallidos": 0})
        siguiente_tema = curso["lecciones"][nueva_leccion]
        mensaje = f"¡Muy bien! Lección completada. ✅\n\nTu siguiente lección es: **{siguiente_tema}**.\n\nGenerando un nuevo reto..."
        responder_mensaje(numero_remitente, mensaje, historial_chat)
        generar_y_enviar_reto(numero_remitente, usuario, curso_key, "Fácil", siguiente_tema)
    else:
        mensaje_final = f"¡Increíble, {usuario['nombre']}! 🏆 ¡Has completado el curso *{curso['nombre']}*! Has demostrado una gran habilidad. ¡Sigue practicando con retos aleatorios!"
        responder_mensaje(numero_remitente, mensaje_final, historial_chat)
        db.actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal", "curso_actual": None})
        enviar_menu_interactivo(numero_remitente)

def procesar_fallo(numero_remitente, usuario, historial_chat):
    intentos = usuario.get("intentos_fallidos", 0) + 1
    db.actualizar_usuario(numero_remitente, {"intentos_fallidos": intentos})

    if usuario.get("estado_conversacion") == "en_curso" and intentos >= UMBRAL_DE_FALLOS:
        db.actualizar_usuario(numero_remitente, {"estado_conversacion": "esperando_ayuda_teorica"})
        tema = CURSOS[usuario["curso_actual"]]["lecciones"][usuario["leccion_actual"]]
        mensaje = f"He notado que este reto te está costando un poco. El tema de esta lección es '{tema}'. ¿Te gustaría una explicación teórica antes de volver a intentarlo? (Responde 'sí' o 'no')"
        responder_mensaje(numero_remitente, mensaje, historial_chat)

def handle_ayuda_teorica(mensaje_texto, numero_remitente, usuario, historial_chat):
    mensaje_lower = mensaje_texto.lower()
    if "sí" in mensaje_lower or "si" in mensaje_lower:
        curso = CURSOS[usuario["curso_actual"]]
        tema = curso["lecciones"][usuario["leccion_actual"]]
        explicacion = ai.explicar_tema_con_ia(tema)
        responder_mensaje(numero_remitente, explicacion, historial_chat)
        responder_mensaje(numero_remitente, "Ahora que hemos repasado, ¡vamos a intentarlo con un nuevo reto sobre el mismo tema!", historial_chat)
        db.actualizar_usuario(numero_remitente, {"intentos_fallidos": 0, "estado_conversacion": "en_curso"})
        generar_y_enviar_reto(numero_remitente, usuario, usuario["curso_actual"], "Fácil", tema)
    else:
        db.actualizar_usuario(numero_remitente, {"estado_conversacion": "en_curso"})
        responder_mensaje(numero_remitente, "¡De acuerdo! Puedes seguir intentando el reto actual cuando quieras. ¡Tú puedes!", historial_chat)

def rendirse(numero_remitente, usuario, historial_chat):
    if not usuario.get("reto_actual_solucion"):
        responder_mensaje(numero_remitente, "Tranquilo, no tienes ningún reto activo para rendirte. ¡Pide uno cuando quieras! 👍", historial_chat)
    else:
        solucion = usuario.get("reto_actual_solucion")
        mensaje_final = f"¡No te preocupes! Rendirse es parte de aprender. Lo importante es entender cómo funciona. 💪\n\nAquí tienes la solución ideal:\n\n```\n{solucion}\n```\n\n¡Analízala y verás que la próxima vez lo conseguirás! Sigue practicando. ✨"
        db.actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal", "reto_actual_enunciado": None, "reto_actual_solucion": None, "curso_actual": None, "intentos_fallidos": 0})
        responder_mensaje(numero_remitente, mensaje_final, historial_chat)
        enviar_menu_interactivo(numero_remitente)

def mostrar_perfil(numero_remitente, usuario, historial_chat):
    perfil = (f"📊 *Tu Perfil de LogicBot*\n\n"
              f"👤 *Nombre:* {usuario['nombre']}\n"
              f"🎓 *Nivel:* {usuario['nivel']}\n"
              f"⭐ *Puntos:* {usuario.get('puntos', 0)} / {PUNTOS_PARA_NIVEL_UP * usuario.get('nivel', 1)}\n"
              f"🔥 *Racha:* {usuario.get('racha_dias', 0)} día(s)")
    responder_mensaje(numero_remitente, perfil, historial_chat)

def generar_y_enviar_reto(numero_remitente, usuario, tipo_reto, dificultad, tematica=None):
    reto = ai.generar_reto_con_ia(usuario['nivel'], tipo_reto, dificultad, tematica)
    historial_chat = json.loads(usuario.get("historial_chat", "[]"))
    
    if "error" in reto:
        responder_mensaje(numero_remitente, reto["error"], historial_chat)
        db.actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal"})
    else:
        db.actualizar_usuario(numero_remitente, {
            "estado_conversacion": "resolviendo_reto" if not usuario.get("curso_actual") else "en_curso",
            "reto_actual_enunciado": reto["enunciado"],
            "reto_actual_solucion": reto["solucion_ideal"],
            "reto_actual_pistas": json.dumps(reto["pistas"]),
            "pistas_usadas": 0,
            "tipo_reto_actual": tipo_reto,
            "dificultad_reto_actual": dificultad
        })
        responder_mensaje(numero_remitente, reto["enunciado"], historial_chat)