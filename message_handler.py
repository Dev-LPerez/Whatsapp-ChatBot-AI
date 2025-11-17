# message_handler.py

import json
import random
import database as db
import ai_services as ai
from config import (
    CURSOS, UMBRAL_DE_FALLOS, PUNTOS_POR_DIFICULTAD,
    PUNTOS_PARA_NIVEL_UP, PUNTOS_HABILIDAD_PARA_NIVEL_UP,
    NOMBRES_NIVELES
)
from whatsapp_utils import responder_mensaje, enviar_menu_interactivo, enviar_botones_basicos, enviar_menu_temas_java
from utils.formatters import (
    formatear_puntos_ganados, formatear_nivel_up,
    formatear_progreso_tema, formatear_error_con_pista,
    formatear_menu_ayuda, generar_barra_progreso
)
from utils.emojis import *
from message_components import (
    handle_onboarding_paso_1, handle_onboarding_paso_2,
    completar_onboarding, finalizar_onboarding_y_empezar,
    verificar_y_otorgar_logros, mostrar_logros_usuario
)

# --- MANEJADORES DE MENSAJES INTERACTIVOS (BOTONES/MENÚS) ---

def handle_interactive_message(id_seleccion, numero_remitente, usuario):
    historial_chat = json.loads(usuario.get("historial_chat", "[]"))

    # === ONBOARDING ===
    if id_seleccion == 'onboarding_empezar':
        handle_onboarding_paso_1(numero_remitente)

    elif id_seleccion in ['nivel_principiante', 'nivel_intermedio', 'nivel_avanzado']:
        nivel = id_seleccion.replace('nivel_', '')
        handle_onboarding_paso_2(numero_remitente, nivel)

    elif id_seleccion in ['pref_curso', 'pref_retos', 'pref_ambos']:
        preferencia = id_seleccion.replace('pref_', '')
        completar_onboarding(numero_remitente, preferencia)

    elif id_seleccion == 'finalizar_onboarding':
        finalizar_onboarding_y_empezar(numero_remitente, usuario)

    # === MENÚ PRINCIPAL ===
    elif id_seleccion == 'mostrar_menu':
        enviar_menu_interactivo(numero_remitente)
    
    # === CURSO JAVA ===
    elif id_seleccion == "mostrar_temas_java":
        enviar_menu_temas_java(numero_remitente)
    
    elif id_seleccion.startswith("iniciar_leccion_"):
        numero_leccion = int(id_seleccion.split("_")[-1])
        iniciar_curso(numero_remitente, usuario, "java", leccion_especifica=numero_leccion)

    elif id_seleccion == "pedir_reto_aleatorio":
        db.actualizar_usuario(numero_remitente, {"estado_conversacion": "eligiendo_dificultad", "tipo_reto_actual": "java"})
        mensaje = f"{PREGUNTA} ¿Qué nivel de dificultad prefieres?\n\n"
        mensaje += f"1{NIVEL_UP} Fácil {FACIL}\n"
        mensaje += f"2{NIVEL_UP} Intermedio {INTERMEDIO}\n"
        mensaje += f"3{NIVEL_UP} Difícil {DIFICIL}"
        responder_mensaje(numero_remitente, mensaje, historial_chat)

    elif id_seleccion == "ver_mi_perfil":
        mostrar_perfil(numero_remitente, usuario, historial_chat)

    elif id_seleccion == "ver_logros":
        mostrar_logros_usuario(numero_remitente, usuario)

# --- MANEJADORES DE MENSAJES DE TEXTO POR ESTADO ---

def handle_text_message(mensaje_texto, numero_remitente, usuario):
    historial_chat = json.loads(usuario.get("historial_chat", "[]"))
    historial_chat.append({"usuario": mensaje_texto})
    estado = usuario.get("estado_conversacion", "menu_principal")
    mensaje_lower = mensaje_texto.lower()

    # Comandos Globales
    if mensaje_lower in ["menu", "menú"]:
        enviar_menu_interactivo(numero_remitente)
        return
    if mensaje_lower == "me rindo":
        rendirse(numero_remitente, usuario, historial_chat)
        return
    if mensaje_lower in ["mi perfil", "perfil"]:
        mostrar_perfil(numero_remitente, usuario, historial_chat)
        return
    if mensaje_lower in ["logros", "mis logros"]:
        mostrar_logros_usuario(numero_remitente, usuario)
        return
    if mensaje_lower in ["ayuda", "pista", "help"]:
        if usuario.get("reto_actual_enunciado"):
            # Dar pista si hay un reto activo
            mensaje_ayuda = f"{IDEA} *Pista:*\n\nRevisa bien la lógica del problema. "
            mensaje_ayuda += "¿Qué tipo de dato necesitas? ¿Qué operaciones son necesarias?"
            responder_mensaje(numero_remitente, mensaje_ayuda, historial_chat)
        else:
            mensaje_ayuda = formatear_menu_ayuda()
            responder_mensaje(numero_remitente, mensaje_ayuda, historial_chat)
        return

    # Lógica por Estado Conversacional
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

# --- ✅ FUNCIÓN MODIFICADA ---
def iniciar_curso(numero_remitente, usuario, curso_key, leccion_especifica=None):
    if curso_key not in CURSOS:
        responder_mensaje(numero_remitente, "Lo siento, ese curso no está disponible.", [])
        return
    
    curso = CURSOS[curso_key]
    # Si se especifica una lección, vamos a ella. Si no, empezamos desde la 0.
    leccion_actual = leccion_especifica if leccion_especifica is not None else 0

    if leccion_actual >= len(curso['lecciones']):
        responder_mensaje(numero_remitente, "Lo siento, esa lección no es válida.", [])
        return

    db.actualizar_usuario(numero_remitente, {
        "estado_conversacion": "en_curso",
        "curso_actual": curso_key,
        "leccion_actual": leccion_actual,
        "intentos_fallidos": 0
    })
    
    tema_seleccionado = curso['lecciones'][leccion_actual]
    mensaje_inicio = f"¡Perfecto! 🎉 Vamos a practicar con el tema: **{tema_seleccionado}**.\n\nGenerando tu reto..."
    historial_chat = json.loads(usuario.get("historial_chat", "[]"))
    responder_mensaje(numero_remitente, mensaje_inicio, historial_chat)
    
    # Generamos el reto para el tema seleccionado
    generar_y_enviar_reto(numero_remitente, usuario, curso_key, "Fácil", tema_seleccionado)


def handle_seleccion_dificultad(mensaje_texto, numero_remitente, usuario, historial_chat):
    dificultad = None
    mensaje_lower = mensaje_texto.lower()
    if "1" in mensaje_texto or "fácil" in mensaje_lower: dificultad = "Fácil"
    elif "2" in mensaje_texto or "intermedio" in mensaje_lower: dificultad = "Intermedio"
    elif "3" in mensaje_texto or "difícil" in mensaje_lower: dificultad = "Difícil"
    
    if dificultad:
        tipo_reto = usuario["tipo_reto_actual"]
        # Para retos aleatorios, elegimos una temática al azar de las lecciones del curso
        tematica_aleatoria = random.choice(CURSOS["java"]["lecciones"])
        responder_mensaje(numero_remitente, f"¡Entendido! 👨‍💻 Buscando un reto de *{tipo_reto}* sobre *{tematica_aleatoria}* con dificultad *{dificultad}*...", historial_chat)
        generar_y_enviar_reto(numero_remitente, usuario, tipo_reto, dificultad, tematica_aleatoria)
    else:
        respuesta_chat = ai.chat_conversacional_con_ia(mensaje_texto, historial_chat, "elección de dificultad")
        responder_mensaje(numero_remitente, respuesta_chat, historial_chat)

def handle_solucion_reto(mensaje_texto, numero_remitente, usuario, historial_chat):
    tipo_reto = usuario.get("curso_actual") or usuario.get("tipo_reto_actual")
    feedback = ai.evaluar_solucion_con_ia(usuario["reto_actual_enunciado"], mensaje_texto, tipo_reto)
    
    if "[PREGUNTA]" in feedback:
        tema_actual = "programación en Java"
        if usuario.get("curso_actual"):
            tema_actual = CURSOS[usuario["curso_actual"]]["lecciones"][usuario["leccion_actual"]]
        respuesta_conversacional = ai.chat_conversacional_con_ia(mensaje_texto, historial_chat, tema_actual)
        responder_mensaje(numero_remitente, respuesta_conversacional, historial_chat)
    
    elif feedback.strip().upper().startswith("✅"):
        responder_mensaje(numero_remitente, feedback, historial_chat)
        procesar_acierto(numero_remitente, usuario, historial_chat)
    else:
        responder_mensaje(numero_remitente, feedback, historial_chat)
        procesar_fallo(numero_remitente, usuario, historial_chat)
        
def procesar_acierto(numero_remitente, usuario, historial_chat):
    dificultad = usuario.get("dificultad_reto_actual", "Fácil")
    puntos_ganados = PUNTOS_POR_DIFICULTAD.get(dificultad, 5)
    racha = usuario.get("racha_dias", 1)
    puntos_con_bonus = puntos_ganados + racha
    
    # Actualizar puntos y stats
    puntos_actuales_generales = usuario.get("puntos", 0) + puntos_con_bonus
    retos_completados = usuario.get("retos_completados", 0) + 1

    # Verificar si fue sin pistas
    pistas_usadas = usuario.get("pistas_usadas", 0)
    retos_sin_pistas = usuario.get("retos_sin_pistas", 0)
    if pistas_usadas == 0:
        retos_sin_pistas += 1

    db.actualizar_usuario(numero_remitente, {
        "puntos": puntos_actuales_generales,
        "retos_completados": retos_completados,
        "retos_sin_pistas": retos_sin_pistas
    })

    # Mensaje de puntos formateado visualmente
    mensaje_puntos = formatear_puntos_ganados(puntos_ganados, racha)
    responder_mensaje(numero_remitente, mensaje_puntos, historial_chat)

    # Actualizar progreso del tema
    tema_actual = usuario.get("tematica_actual")
    if tema_actual:
        progreso_temas = json.loads(usuario.get("progreso_temas", "{}"))
        
        if tema_actual not in progreso_temas:
            progreso_temas[tema_actual] = {"puntos": 0, "nivel": 1}

        tema_progreso = progreso_temas[tema_actual]
        tema_progreso["puntos"] += puntos_con_bonus
        
        # Mostrar barra de progreso del tema
        puntos_necesarios = PUNTOS_HABILIDAD_PARA_NIVEL_UP * tema_progreso["nivel"]
        mensaje_tema = formatear_progreso_tema(
            tema_actual,
            tema_progreso["puntos"],
            tema_progreso["nivel"],
            puntos_necesarios
        )
        responder_mensaje(numero_remitente, mensaje_tema, historial_chat)

        # Verificar level up del tema
        if tema_progreso["puntos"] >= puntos_necesarios:
            tema_progreso["nivel"] += 1
            mensaje_nivel_tema = f"\n{CELEBRACION} ¡Subiste de nivel en *{tema_actual}*!\n"
            mensaje_nivel_tema += f"Ahora eres *Nivel {tema_progreso['nivel']}* {ESTRELLA}"
            responder_mensaje(numero_remitente, mensaje_nivel_tema, historial_chat)
            
        db.actualizar_usuario(numero_remitente, {"progreso_temas": json.dumps(progreso_temas)})

    # Verificar level up general
    nivel_actual = usuario.get("nivel", 1)
    if puntos_actuales_generales >= PUNTOS_PARA_NIVEL_UP * nivel_actual:
        nuevo_nivel_general = nivel_actual + 1
        nombre_nivel = NOMBRES_NIVELES.get(nuevo_nivel_general, f"Nivel {nuevo_nivel_general}")

        db.actualizar_usuario(numero_remitente, {"nivel": nuevo_nivel_general})

        mensaje_nivel_up = formatear_nivel_up(nuevo_nivel_general, nombre_nivel)
        responder_mensaje(numero_remitente, mensaje_nivel_up, historial_chat)

    # Verificar y otorgar logros
    usuario_actualizado = db.obtener_usuario(numero_remitente)
    verificar_y_otorgar_logros(numero_remitente, usuario_actualizado)

    # Volver al menú principal
    db.actualizar_usuario(numero_remitente, {
        "estado_conversacion": "menu_principal",
        "reto_actual_enunciado": None,
        "reto_actual_solucion": None,
        "pistas_usadas": 0
    })

    # Menú con botones
    mensaje_final = f"\n{PREGUNTA} ¿Qué quieres hacer ahora?"
    botones = [
        {"id": "pedir_reto_aleatorio", "title": f"Otro reto {COHETE}"},
        {"id": "mostrar_menu", "title": f"Ver menú {MENU}"}
    ]
    enviar_botones_basicos(numero_remitente, mensaje_final, botones)


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
    nombre = usuario['nombre']
    nivel = usuario.get('nivel', 1)
    puntos = usuario.get('puntos', 0)
    racha = usuario.get('racha_dias', 0)
    retos_completados = usuario.get('retos_completados', 0)

    # Nombre del nivel
    nombre_nivel = NOMBRES_NIVELES.get(nivel, f"Nivel {nivel}")

    # Puntos para próximo nivel
    puntos_necesarios = PUNTOS_PARA_NIVEL_UP * nivel
    barra_nivel = generar_barra_progreso(puntos, puntos_necesarios, 10)

    perfil_general = f"{PERFIL} *TU PERFIL*\n\n"
    perfil_general += f"{ROBOT} {nombre}\n"
    perfil_general += f"{TROFEO} {nombre_nivel}\n\n"
    perfil_general += f"━━━━━━━━━━━━\n"
    perfil_general += f"{ESTRELLA} *Puntos:* {puntos}/{puntos_necesarios}\n"
    perfil_general += f"{barra_nivel}\n\n"
    perfil_general += f"{RACHA} *Racha:* {racha} día(s)\n"
    perfil_general += f"{RETO} *Retos completados:* {retos_completados}\n"
    perfil_general += f"━━━━━━━━━━━━\n"

    responder_mensaje(numero_remitente, perfil_general, historial_chat)

    # Progreso por habilidades
    progreso_temas = json.loads(usuario.get("progreso_temas", "{}"))

    if progreso_temas and any(data['puntos'] > 0 for data in progreso_temas.values()):
        mensaje_habilidades = f"\n{CONCEPTO} *PROGRESO POR TEMA:*\n\n"

        for tema, data in progreso_temas.items():
            if data['puntos'] > 0:
                puntos_necesarios_tema = PUNTOS_HABILIDAD_PARA_NIVEL_UP * data['nivel']
                barra_tema = generar_barra_progreso(data['puntos'], puntos_necesarios_tema, 8)

                mensaje_habilidades += f"*{tema}*\n"
                mensaje_habilidades += f"Nivel {data['nivel']} | {barra_tema}\n"
                mensaje_habilidades += f"{data['puntos']}/{puntos_necesarios_tema} pts\n\n"

        responder_mensaje(numero_remitente, mensaje_habilidades, historial_chat)
    else:
        mensaje_no_progreso = f"\n{IDEA} Aún no has practicado ningún tema.\n¡Empieza un reto para ver tu progreso!"
        responder_mensaje(numero_remitente, mensaje_no_progreso, historial_chat)

    # Botones de acción
    botones = [
        {"id": "ver_logros", "title": f"Ver logros {LOGRO}"},
        {"id": "mostrar_menu", "title": f"Volver {MENU}"}
    ]
    enviar_botones_basicos(numero_remitente, "", botones)

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
            "dificultad_reto_actual": dificultad,
            "tematica_actual": tematica
        })
        responder_mensaje(numero_remitente, reto["enunciado"], historial_chat)