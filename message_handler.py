# message_handler.py

import json
import random
import time
from datetime import datetime
import database as db
import ai_services as ai
from config import (
    CURSOS, UMBRAL_DE_FALLOS, PUNTOS_POR_DIFICULTAD,
    PUNTOS_PARA_NIVEL_UP, PUNTOS_HABILIDAD_PARA_NIVEL_UP,
    NOMBRES_NIVELES
)
from whatsapp_utils import (
    responder_mensaje, enviar_menu_interactivo, enviar_botones_basicos,
    enviar_menu_temas_java, enviar_lista_recursos
)
from utils.formatters import (
    formatear_puntos_ganados, formatear_nivel_up,
    formatear_progreso_tema, formatear_menu_ayuda, generar_barra_progreso
)
from utils.emojis import *
from message_components import (
    handle_onboarding_paso_1, handle_onboarding_paso_2,
    completar_onboarding, finalizar_onboarding_y_empezar,
    verificar_y_otorgar_logros, mostrar_logros_usuario
)


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
        db.actualizar_usuario(numero_remitente,
                              {"estado_conversacion": "eligiendo_dificultad", "tipo_reto_actual": "java"})
        mensaje = f"{PREGUNTA} ¿Qué nivel de dificultad prefieres?\n\n"
        mensaje += f"1{NIVEL_UP} Fácil {FACIL}\n"
        mensaje += f"2{NIVEL_UP} Intermedio {INTERMEDIO}\n"
        mensaje += f"3{NIVEL_UP} Difícil {DIFICIL}"
        responder_mensaje(numero_remitente, mensaje, historial_chat)

    elif id_seleccion == "ver_mi_perfil":
        mostrar_perfil(numero_remitente, usuario, historial_chat)

    elif id_seleccion == "ver_logros":
        mostrar_logros_usuario(numero_remitente, usuario)

    elif id_seleccion == "ver_coleccion":
        mostrar_biblioteca_fichas(numero_remitente, usuario, historial_chat)

    elif id_seleccion.startswith("ver_ficha_"):
        indice_tema = int(id_seleccion.split("_")[-1])
        if 0 <= indice_tema < len(CURSOS["java"]["lecciones"]):
            tema = CURSOS["java"]["lecciones"][indice_tema]
            responder_mensaje(numero_remitente, f"{LIBRO} Buscando la ficha de *{tema}* en tu mochila...",
                              historial_chat)
            ficha = ai.generar_cheat_sheet(tema)
            responder_mensaje(numero_remitente, ficha, historial_chat)
        else:
            responder_mensaje(numero_remitente, "No encontré esa ficha.", historial_chat)


def handle_text_message(mensaje_texto, numero_remitente, usuario):
    historial_chat = json.loads(usuario.get("historial_chat", "[]"))
    historial_chat.append({"usuario": mensaje_texto})
    estado = usuario.get("estado_conversacion", "menu_principal")
    mensaje_lower = mensaje_texto.lower().strip()

    # --- COMANDO DE VINCULACIÓN A CLASE ---
    if mensaje_lower.startswith("unirse"):
        partes = mensaje_texto.split()
        if len(partes) > 1:
            token = partes[1].upper().strip()
            # Llamamos a la nueva función de BD
            exito = db.vincular_alumno_a_clase(numero_remitente, token)
            if exito:
                responder_mensaje(numero_remitente,
                                  f"✅ ¡Conectado! Ahora estás vinculado a la clase *{token}*.\nTu profesor podrá ver tu progreso.",
                                  historial_chat)
            else:
                responder_mensaje(numero_remitente, "❌ Hubo un error al unirte. Intenta de nuevo.", historial_chat)
        else:
            responder_mensaje(numero_remitente,
                              f"⚠️ Formato incorrecto.\nUsa: *unirse CÓDIGO*\nEjemplo: unirse PROG-2025-A",
                              historial_chat)
        return

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
    if mensaje_lower in ["fichas", "mochila", "recursos"]:
        mostrar_biblioteca_fichas(numero_remitente, usuario, historial_chat)
        return
    if mensaje_lower in ["ayuda", "pista", "help"]:
        if usuario.get("reto_actual_enunciado"):
            # 1. Recuperar las pistas específicas de este reto y el contador actual
            pistas_guardadas = json.loads(usuario.get("reto_actual_pistas", "[]"))
            pistas_usadas = usuario.get("pistas_usadas", 0)

            # 2. Verificar si quedan pistas disponibles
            if pistas_usadas < len(pistas_guardadas):
                pista_a_mostrar = pistas_guardadas[pistas_usadas]

                # --- ACTUALIZACIÓN: CONTADOR GLOBAL Y ACTUAL ---
                # Obtener el usuario actualizado para tener el valor más reciente
                usuario_actual = db.obtener_usuario(numero_remitente)
                total_pistas = usuario_actual.get("total_pistas_usadas", 0) + 1

                db.actualizar_usuario(numero_remitente, {
                    "pistas_usadas": pistas_usadas + 1,
                    "total_pistas_usadas": total_pistas  # Contador histórico global
                })
                # --------------------------

                mensaje_ayuda = f"{IDEA} *Pista #{pistas_usadas + 1}:*\n\n{pista_a_mostrar}"

                # Opcional: Advertencia si es la última pista
                if pistas_usadas + 1 == len(pistas_guardadas):
                    mensaje_ayuda += "\n\n⚠️ *¡Ojo!* Esta es tu última pista."

            else:
                # Si ya agotó las pistas (usualmente son 3)
                mensaje_ayuda = f"{CANDADO} Ya has utilizado todas las pistas disponibles para este reto.\n¡Confío en que puedes resolverlo! {PRACTICA}"

            responder_mensaje(numero_remitente, mensaje_ayuda, historial_chat)
        else:
            mensaje_ayuda = formatear_menu_ayuda()
            responder_mensaje(numero_remitente, mensaje_ayuda, historial_chat)
        return

    # Lógica por Estado Conversacional
    # --- NUEVOS ESTADOS FASE 3 ---
    if estado == "esperando_defensa":
        handle_respuesta_defensa(mensaje_texto, numero_remitente, usuario, historial_chat)
    elif estado == "resolviendo_debug":
        # Reutilizamos la lógica de solución pero sabiendo que es debug
        handle_solucion_reto(mensaje_texto, numero_remitente, usuario, historial_chat, es_debug=True)
    # --- ESTADOS EXISTENTES ---
    elif estado == "eligiendo_dificultad":
        handle_seleccion_dificultad(mensaje_texto, numero_remitente, usuario, historial_chat)
    elif estado in ["en_curso", "resolviendo_reto"]:
        handle_solucion_reto(mensaje_texto, numero_remitente, usuario, historial_chat)
    elif estado == "esperando_ayuda_teorica":
        handle_ayuda_teorica(mensaje_texto, numero_remitente, usuario, historial_chat)
    else:
        respuesta_chat = ai.chat_conversacional_con_ia(mensaje_texto, historial_chat)
        responder_mensaje(numero_remitente, respuesta_chat, historial_chat)


def mostrar_biblioteca_fichas(numero_remitente, usuario, historial_chat):
    progreso_temas = json.loads(usuario.get("progreso_temas", "{}"))
    fichas_disponibles = []

    temas_curso = CURSOS["java"]["lecciones"]

    for idx, tema in enumerate(temas_curso):
        data_tema = progreso_temas.get(tema, {"nivel": 1})
        if data_tema["nivel"] > 1:
            fichas_disponibles.append((idx, tema))

    if not fichas_disponibles:
        mensaje = f"{TRISTE} Tu mochila está vacía.\n\n"
        mensaje += "Para desbloquear Fichas Técnicas, completa retos y sube de nivel en los temas.\n"
        mensaje += f"¡Ve a *{COHETE} Aprender* para conseguir tu primera ficha!"
        responder_mensaje(numero_remitente, mensaje, historial_chat)
        enviar_menu_interactivo(numero_remitente)
    else:
        enviar_lista_recursos(numero_remitente, fichas_disponibles)


def iniciar_curso(numero_remitente, usuario, curso_key, leccion_especifica=None):
    if curso_key not in CURSOS:
        responder_mensaje(numero_remitente, "Lo siento, ese curso no está disponible.", [])
        return

    curso = CURSOS[curso_key]
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
    historial_chat = json.loads(usuario.get("historial_chat", "[]"))

    mensaje_inicio = f"{COHETE} ¡Excelente elección! Vamos a dominar el tema: *{tema_seleccionado}*."
    responder_mensaje(numero_remitente, mensaje_inicio, historial_chat)

    mensaje_cargando = f"{LIBRO} Preparando tu mini-clase sobre {tema_seleccionado}..."
    responder_mensaje(numero_remitente, mensaje_cargando, historial_chat)

    time.sleep(1)
    explicacion = ai.generar_introduccion_tema(tema_seleccionado)
    responder_mensaje(numero_remitente, explicacion, historial_chat)

    time.sleep(2)
    mensaje_reto = f"{PRACTICA} Ahora que sabes la teoría, ¡vamos a ponerlo en práctica con un reto!"
    responder_mensaje(numero_remitente, mensaje_reto, historial_chat)

    generar_y_enviar_reto(numero_remitente, usuario, curso_key, "Fácil", tema_seleccionado)


def handle_seleccion_dificultad(mensaje_texto, numero_remitente, usuario, historial_chat):
    dificultad = None
    mensaje_lower = mensaje_texto.lower()
    if "1" in mensaje_texto or "fácil" in mensaje_lower:
        dificultad = "Fácil"
    elif "2" in mensaje_texto or "intermedio" in mensaje_lower:
        dificultad = "Intermedio"
    elif "3" in mensaje_texto or "difícil" in mensaje_lower:
        dificultad = "Difícil"

    if dificultad:
        tipo_reto = usuario["tipo_reto_actual"]
        tematica_aleatoria = random.choice(CURSOS["java"]["lecciones"])
        responder_mensaje(numero_remitente,
                          f"¡Entendido! 👨‍💻 Buscando un reto de *{tipo_reto}* sobre *{tematica_aleatoria}* con dificultad *{dificultad}*...",
                          historial_chat)
        generar_y_enviar_reto(numero_remitente, usuario, tipo_reto, dificultad, tematica_aleatoria)
    else:
        respuesta_chat = ai.chat_conversacional_con_ia(mensaje_texto, historial_chat, "elección de dificultad")
        responder_mensaje(numero_remitente, respuesta_chat, historial_chat)


def handle_solucion_reto(mensaje_texto, numero_remitente, usuario, historial_chat, es_debug=False):
    enunciado = usuario.get("reto_actual_enunciado")

    # 1. EVALUAR PRIMERO CON IA
    tipo_reto = "depuración de código" if es_debug else (usuario.get("curso_actual") or usuario.get("tipo_reto_actual"))
    feedback = ai.evaluar_solucion_con_ia(enunciado, mensaje_texto, tipo_reto)

    # 2. CÁLCULO DE TIEMPO (SILENCIOSO)
    es_sospechoso = False
    tiempo_tomado = 0
    tiempo_esperado = usuario.get("tiempo_estimado_ia", 60)
    timestamp_inicio = usuario.get("timestamp_inicio_reto")

    if timestamp_inicio:
        try:
            inicio = datetime.fromisoformat(timestamp_inicio)
            fin = datetime.now()
            tiempo_tomado = (fin - inicio).total_seconds()

            # Umbral de sospecha: menos del 50% del tiempo estimado
            if tiempo_tomado < (tiempo_esperado / 2):
                es_sospechoso = True
        except ValueError:
            pass

    # 3. LÓGICA DE FILTRADO DE REPORTES (¡AQUÍ ESTÁ LA SOLUCIÓN!)
    # Solo reportamos si es sospechoso Y NO es una pregunta teórica Y el mensaje es lo suficientemente largo
    # o la IA dice que es CORRECTO (copy-paste rápido)
    es_pregunta_teorica = "[PREGUNTA]" in feedback
    es_mensaje_corto = len(mensaje_texto) < 15  # Ignora "Hola", "No se", "Ayuda"
    es_correcto = feedback.strip().upper().startswith("✅")

    # REGISTRAR ALERTA SOLO SI:
    # 1. Es rápido (sospechoso)
    # 2. NO es una pregunta teórica
    # 3. Y ADEMÁS: (Es correcto O es un intento largo de código)
    should_report = es_sospechoso and not es_pregunta_teorica and (es_correcto or not es_mensaje_corto)

    if should_report:
        print(f"🚩 FLAG: {numero_remitente} respondió en {tiempo_tomado:.1f}s (Est: {tiempo_esperado}s)")
        datos_alerta = {
            "nombre": usuario.get("nombre", "Desconocido"),
            "enunciado": enunciado,
            "respuesta": mensaje_texto,
            "tiempo_tomado": round(tiempo_tomado, 2),
            "tiempo_estimado": tiempo_esperado,
            "timestamp_envio": timestamp_inicio
        }
        db.registrar_alerta_seguridad(numero_remitente, datos_alerta)

    # 4. FLUJO DE RESPUESTA AL USUARIO
    if es_pregunta_teorica:
        tema_actual = "programación en Java"
        if usuario.get("curso_actual"):
            tema_actual = CURSOS[usuario["curso_actual"]]["lecciones"][usuario["leccion_actual"]]
        respuesta_conversacional = ai.chat_conversacional_con_ia(mensaje_texto, historial_chat, tema_actual)
        responder_mensaje(numero_remitente, respuesta_conversacional, historial_chat)

    elif es_correcto:
        # Lógica de defensa (Si es sospechoso, activamos defensa obligatoria)
        dificultad = usuario.get("dificultad_reto_actual", "Fácil")
        activar_defensa = es_sospechoso or (dificultad != "Fácil" and not es_debug and random.random() < 0.3)

        if activar_defensa:
            pregunta_defensa = ai.generar_pregunta_defensa(enunciado, mensaje_texto)
            db.actualizar_usuario(numero_remitente, {
                "estado_conversacion": "esperando_defensa",
                "pregunta_defensa_actual": pregunta_defensa,
                "bandera_sospecha_velocidad": es_sospechoso
            })

            if es_sospechoso:
                msg_validacion = f"✅ ¡Código correcto!\n\nPara validar tu aprendizaje y asignarte los puntos, por favor respóndeme esta breve pregunta sobre tu solución:"
            else:
                msg_validacion = f"✅ ¡Bien hecho!\n\nSolo una pregunta rápida para cerrar el tema:"

            responder_mensaje(numero_remitente, msg_validacion, historial_chat)
            time.sleep(1)
            responder_mensaje(numero_remitente, pregunta_defensa, historial_chat)
        else:
            responder_mensaje(numero_remitente, feedback, historial_chat)
            procesar_acierto(numero_remitente, usuario, historial_chat)
    else:
        # Respuesta incorrecta
        responder_mensaje(numero_remitente, feedback, historial_chat)
        procesar_fallo(numero_remitente, usuario, historial_chat)


def procesar_acierto(numero_remitente, usuario, historial_chat, factor_puntos=1.0):
    dificultad = usuario.get("dificultad_reto_actual", "Fácil")

    # Obtenemos los puntos base según dificultad
    puntos_base = PUNTOS_POR_DIFICULTAD.get(dificultad, 10)

    # APLICAMOS EL FACTOR (Aquí está el arreglo) 🛠️
    puntos_ganados = int(puntos_base * factor_puntos)

    racha = usuario.get("racha_dias", 1)
    puntos_con_bonus = puntos_ganados + racha

    puntos_actuales_generales = usuario.get("puntos", 0) + puntos_con_bonus
    retos_completados = usuario.get("retos_completados", 0) + 1
    pistas_usadas = usuario.get("pistas_usadas", 0)
    retos_sin_pistas = usuario.get("retos_sin_pistas", 0)
    if pistas_usadas == 0:
        retos_sin_pistas += 1

    db.actualizar_usuario(numero_remitente, {
        "puntos": puntos_actuales_generales,
        "retos_completados": retos_completados,
        "retos_sin_pistas": retos_sin_pistas
    })

    mensaje_puntos = formatear_puntos_ganados(puntos_ganados, racha)
    responder_mensaje(numero_remitente, mensaje_puntos, historial_chat)

    tema_actual = usuario.get("tematica_actual")
    if tema_actual:
        progreso_temas = json.loads(usuario.get("progreso_temas", "{}"))
        if tema_actual not in progreso_temas:
            progreso_temas[tema_actual] = {"puntos": 0, "nivel": 1}

        tema_data = progreso_temas[tema_actual]
        tema_data["puntos"] += puntos_con_bonus
        puntos_necesarios = PUNTOS_HABILIDAD_PARA_NIVEL_UP * tema_data["nivel"]

        mensaje_tema = formatear_progreso_tema(
            tema_actual, tema_data["puntos"], tema_data["nivel"], puntos_necesarios
        )
        responder_mensaje(numero_remitente, mensaje_tema, historial_chat)

        if tema_data["puntos"] >= puntos_necesarios:
            tema_data["nivel"] += 1
            mensaje_recompensa = f"{CELEBRACION} ¡FELICIDADES! Has subido al Nivel {tema_data['nivel']} en *{tema_actual}*.\n\n"
            mensaje_recompensa += f"🎁 **¡OBJETO DESBLOQUEADO!**\n"
            mensaje_recompensa += f"Has ganado la **Ficha Técnica de {tema_actual}**.\n"
            mensaje_recompensa += "Guárdala en tus mensajes destacados para usarla en el futuro."
            responder_mensaje(numero_remitente, mensaje_recompensa, historial_chat)

            time.sleep(1)
            cheat_sheet = ai.generar_cheat_sheet(tema_actual)
            responder_mensaje(numero_remitente, cheat_sheet, historial_chat)

        db.actualizar_usuario(numero_remitente, {"progreso_temas": json.dumps(progreso_temas)})

    nivel_actual = usuario.get("nivel", 1)
    if puntos_actuales_generales >= PUNTOS_PARA_NIVEL_UP * nivel_actual:
        nuevo_nivel_general = nivel_actual + 1
        nombre_nivel = NOMBRES_NIVELES.get(nuevo_nivel_general, f"Nivel {nuevo_nivel_general}")
        db.actualizar_usuario(numero_remitente, {"nivel": nuevo_nivel_general})
        mensaje_nivel_up = formatear_nivel_up(nuevo_nivel_general, nombre_nivel)
        responder_mensaje(numero_remitente, mensaje_nivel_up, historial_chat)

    usuario_actualizado = db.obtener_usuario(numero_remitente)
    verificar_y_otorgar_logros(numero_remitente, usuario_actualizado)

    db.actualizar_usuario(numero_remitente, {
        "estado_conversacion": "menu_principal",
        "reto_actual_enunciado": None,
        "reto_actual_solucion": None,
        "pistas_usadas": 0
    })

    mensaje_final = f"\n{PREGUNTA} ¿Qué quieres hacer ahora?"
    botones = [
        {"id": "pedir_reto_aleatorio", "title": f"Otro reto {COHETE}"},
        {"id": "mostrar_menu", "title": f"Ver menú {MENU}"}
    ]
    enviar_botones_basicos(numero_remitente, "👇 Opciones disponibles:", botones)


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
    total_fallos_global = usuario.get("total_fallos", 0) + 1  # Contador histórico global

    db.actualizar_usuario(numero_remitente, {
        "intentos_fallidos": intentos,
        "total_fallos": total_fallos_global  # Guardamos histórico
    })

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
        responder_mensaje(numero_remitente,
                          "Ahora que hemos repasado, ¡vamos a intentarlo con un nuevo reto sobre el mismo tema!",
                          historial_chat)
        db.actualizar_usuario(numero_remitente, {"intentos_fallidos": 0, "estado_conversacion": "en_curso"})
        generar_y_enviar_reto(numero_remitente, usuario, usuario["curso_actual"], "Fácil", tema)
    else:
        db.actualizar_usuario(numero_remitente, {"estado_conversacion": "en_curso"})
        responder_mensaje(numero_remitente,
                          "¡De acuerdo! Puedes seguir intentando el reto actual cuando quieras. ¡Tú puedes!",
                          historial_chat)


def rendirse(numero_remitente, usuario, historial_chat):
    if not usuario.get("reto_actual_solucion"):
        responder_mensaje(numero_remitente,
                          "Tranquilo, no tienes ningún reto activo para rendirte. ¡Pide uno cuando quieras! 👍",
                          historial_chat)
    else:
        solucion = usuario.get("reto_actual_solucion")
        mensaje_final = f"¡No te preocupes! Rendirse es parte de aprender. Lo importante es entender cómo funciona. 💪\n\nAquí tienes la solución ideal:\n\n```\n{solucion}\n```\n\n¡Analízala y verás que la próxima vez lo conseguirás! Sigue practicando. ✨"
        db.actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal", "reto_actual_enunciado": None,
                                                 "reto_actual_solucion": None, "curso_actual": None,
                                                 "intentos_fallidos": 0})
        responder_mensaje(numero_remitente, mensaje_final, historial_chat)
        enviar_menu_interactivo(numero_remitente)


def mostrar_perfil(numero_remitente, usuario, historial_chat):
    nombre = usuario['nombre']
    nivel = usuario.get('nivel', 1)
    puntos = usuario.get('puntos', 0)
    racha = usuario.get('racha_dias', 0)
    retos_completados = usuario.get('retos_completados', 0)

    nombre_nivel = NOMBRES_NIVELES.get(nivel, f"Nivel {nivel}")
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

    botones = [
        {"id": "ver_logros", "title": f"Ver logros {LOGRO}"},
        {"id": "mostrar_menu", "title": f"Volver {MENU}"}
    ]
    enviar_botones_basicos(numero_remitente, "👇 Opciones disponibles:", botones)


def generar_y_enviar_reto(numero_remitente, usuario, tipo_reto, dificultad, tematica=None):
    # 30% de probabilidad de que sea un Reto de Depuración (si no es el primer reto)
    es_debug = random.random() < 0.3 and usuario.get("retos_completados", 0) > 2

    historial_chat = json.loads(usuario.get("historial_chat", "[]"))

    if es_debug:
        reto = ai.generar_reto_depuracion(usuario['nivel'], tematica or "Java General")
        nuevo_estado = "resolviendo_debug"
        tipo_msg = f"🕵️ *RETO DE DEPURACIÓN*"
    else:
        reto = ai.generar_reto_con_ia(usuario['nivel'], tipo_reto, dificultad, tematica)
        nuevo_estado = "resolviendo_reto" if not usuario.get("curso_actual") else "en_curso"
        tipo_msg = f"{RETO} *NUEVO RETO ({dificultad})*"

    if "error" in reto:
        responder_mensaje(numero_remitente, "Ups, la IA se tomó un descanso. Intenta de nuevo.", historial_chat)
        db.actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal"})
    else:
        # 🕒 OBTENEMOS TIMESTAMP ACTUAL PARA EL DETECTOR DE VELOCIDAD
        ahora = datetime.now().isoformat()

        # Guardamos el reto
        db.actualizar_usuario(numero_remitente, {
            "estado_conversacion": nuevo_estado,
            "reto_actual_enunciado": reto["enunciado"],
            "reto_actual_solucion": reto["solucion_ideal"],
            "reto_actual_pistas": json.dumps(reto["pistas"]),
            "pistas_usadas": 0,

            # --- NUEVOS CAMPOS DE TIEMPO ---
            "timestamp_inicio_reto": ahora,
            "tiempo_estimado_ia": reto.get("tiempo_estimado", 120),  # Default 2 min si falla
            # -------------------------------

            "tipo_reto_actual": "debug" if es_debug else tipo_reto,
            "dificultad_reto_actual": dificultad,
            "tematica_actual": tematica
        })

        msg_completo = f"{tipo_msg}\n\n{reto['enunciado']}"
        responder_mensaje(numero_remitente, msg_completo, historial_chat)


# --- ✅ NUEVA FUNCIÓN FASE 3: PROCESAR RESPUESTA DE DEFENSA ---

def handle_respuesta_defensa(mensaje_texto, numero_remitente, usuario, historial_chat):
    """Evalúa si el estudiante realmente comprende su solución (anti-plagio)."""
    pregunta = usuario.get("pregunta_defensa_actual", "¿Por qué?")
    enunciado = usuario.get("reto_actual_enunciado", "")

    responder_mensaje(numero_remitente, f"🤔 Analizando tu justificación...", historial_chat)

    es_valido = ai.evaluar_defensa(pregunta, mensaje_texto, enunciado)

    if es_valido:
        responder_mensaje(numero_remitente, f"✅ ¡Explicación válida! Has demostrado dominio.", historial_chat)
        # 1.0 es el valor por defecto, puntos completos
        procesar_acierto(numero_remitente, usuario, historial_chat)
    else:
        msg_fail = f"❌ Mmm, esa explicación no cuadra con tu código.\n"
        msg_fail += "Te daré la mitad de los puntos esta vez, pero asegúrate de entender lo que escribes."
        responder_mensaje(numero_remitente, msg_fail, historial_chat)

        # CORRECCIÓN AQUÍ: Pasamos 0.5 para dar la mitad de puntos
        procesar_acierto(numero_remitente, usuario, historial_chat, factor_puntos=0.5)