# main.py (LogicBot v5.0 - Menú Interactivo)

import json
from fastapi import FastAPI, Request, Response
from datetime import date

import database as db
import ai_services as ai
from whatsapp_utils import responder_mensaje, enviar_menu_interactivo

app = FastAPI()

CURSOS = {
    "python": {
        "nombre": "Python Essentials 🐍",
        "lecciones": ["Variables y Tipos de Datos", "Operadores Aritméticos", "Condicionales (if/else)", "Bucles (for y while)", "Funciones"]
    }
}
UMBRAL_DE_FALLOS = 2

def manejar_seleccion_menu(id_seleccion, numero_remitente, usuario):
    """Procesa la opción que el usuario eligió del menú interactivo."""
    historial_chat = json.loads(usuario.get("historial_chat", "[]"))
    
    if id_seleccion == "iniciar_curso_python":
        curso = CURSOS["python"]
        leccion_actual = 0
        db.actualizar_usuario(numero_remitente, {"estado_conversacion": "en_curso", "curso_actual": "python", "leccion_actual": leccion_actual, "intentos_fallidos": 0})
        mensaje_inicio = (f"¡Excelente decisión! 🎉 Has iniciado el curso: *{curso['nombre']}*.\n\nTu primera lección es sobre **{curso['lecciones'][leccion_actual]}**.\n\nEstoy generando tu primer reto. ¡Dame un segundo! 👨‍💻")
        responder_mensaje(numero_remitente, mensaje_inicio, historial_chat)
        tematica = curso['lecciones'][leccion_actual]
        reto = ai.generar_reto_con_ia(usuario['nivel'], "Python", "Fácil", tematica)
        if "error" in reto:
            responder_mensaje(numero_remitente, reto["error"], historial_chat)
            db.actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal"})
        else:
            db.actualizar_usuario(numero_remitente, {"reto_actual_enunciado": reto["enunciado"], "reto_actual_solucion": reto["solucion_ideal"], "reto_actual_pistas": json.dumps(reto["pistas"]), "pistas_usadas": 0, "reto_actual_tipo": "Python"})
            responder_mensaje(numero_remitente, reto["enunciado"], historial_chat)

    elif id_seleccion == "pedir_reto_aleatorio":
        db.actualizar_usuario(numero_remitente, {"curso_actual": None, "estado_conversacion": "eligiendo_dificultad", "tipo_reto_actual": "Python"})
        responder_mensaje(numero_remitente, "¿Qué nivel de dificultad prefieres? 🤔\n\n1. Fácil 🌱\n2. Intermedio 🔥\n3. Difícil 🤯", historial_chat)

    elif id_seleccion == "ver_mi_perfil":
        perfil = (f"📊 *Tu Perfil de LogicBot*\n\n👤 *Nombre:* {usuario['nombre']}\n🎓 *Nivel:* {usuario['nivel']}\n⭐ *Puntos:* {usuario.get('puntos', 0)}\n🔥 *Racha:* {usuario.get('racha_dias', 0)} día(s)")
        responder_mensaje(numero_remitente, perfil, historial_chat)

@app.post("/webhook")
async def recibir_mensaje(request: Request):
    body = await request.json()
    print(json.dumps(body, indent=2))
    try:
        value = body['entry'][0]['changes'][0]['value']
        if not (value.get("messages") and value['messages'][0]): return Response(status_code=200)
        
        message_data = value['messages'][0]
        numero_remitente = message_data['from']
        nombre_usuario = value['contacts'][0]['profile']['name']

        usuario = db.obtener_usuario(numero_remitente)
        
        if not usuario:
            db.crear_usuario(numero_remitente, nombre_usuario)
            usuario = db.obtener_usuario(numero_remitente)
            bienvenida = (f"¡Hola, {nombre_usuario}! 👋 Soy LogicBot.\n\nEscribe `menu` para ver todo lo que puedo hacer por ti. 🚀")
            responder_mensaje(numero_remitente, bienvenida, [])
            return Response(status_code=200)

        if usuario.get("ultima_conexion") != str(date.today()):
            ayer = date.fromisoformat(usuario.get("ultima_conexion", "1970-01-01"))
            racha = usuario.get("racha_dias", 0) if (date.today() - ayer).days == 1 else 0
            db.actualizar_usuario(numero_remitente, {"ultima_conexion": str(date.today()), "racha_dias": racha + 1})
            usuario["racha_dias"] = racha + 1

        if message_data.get('type') == 'interactive':
            if message_data['interactive']['type'] == 'list_reply':
                id_seleccion = message_data['interactive']['list_reply']['id']
                manejar_seleccion_menu(id_seleccion, numero_remitente, usuario)
            return Response(status_code=200)

        mensaje_texto = message_data['text']['body']
        historial_chat = json.loads(usuario.get("historial_chat", "[]"))
        historial_chat.append({"usuario": mensaje_texto})
        estado = usuario.get("estado_conversacion", "menu_principal")
        mensaje_lower = mensaje_texto.lower()

        if mensaje_lower == "menu":
            enviar_menu_interactivo(numero_remitente)

        elif "empezar curso" in mensaje_lower:
            manejar_seleccion_menu("iniciar_curso_python", numero_remitente, usuario)

        elif estado == "esperando_ayuda_teorica":
            curso = CURSOS[usuario["curso_actual"]]
            tema = curso["lecciones"][usuario["leccion_actual"]]
            if "sí" in mensaje_lower or "si" in mensaje_lower:
                explicacion = ai.explicar_tema_con_ia(tema)
                responder_mensaje(numero_remitente, explicacion, historial_chat)
                responder_mensaje(numero_remitente, "Ahora que hemos repasado, ¡vamos a intentarlo con un nuevo reto sobre el mismo tema!", historial_chat)
                db.actualizar_usuario(numero_remitente, {"intentos_fallidos": 0, "estado_conversacion": "en_curso"})
                reto = ai.generar_reto_con_ia(usuario['nivel'], "Python", "Fácil", tema)
                if "error" in reto:
                    responder_mensaje(numero_remitente, reto["error"], historial_chat)
                else:
                    db.actualizar_usuario(numero_remitente, {"reto_actual_enunciado": reto["enunciado"], "reto_actual_solucion": reto["solucion_ideal"], "reto_actual_pistas": json.dumps(reto["pistas"]), "pistas_usadas": 0})
                    responder_mensaje(numero_remitente, reto["enunciado"], historial_chat)
            else:
                db.actualizar_usuario(numero_remitente, {"estado_conversacion": "en_curso"})
                responder_mensaje(numero_remitente, "¡De acuerdo! Puedes seguir intentando el reto actual cuando quieras.", historial_chat)

        elif mensaje_lower.startswith("reto"):
            db.actualizar_usuario(numero_remitente, {"curso_actual": None})
            tipo_reto, tematica = "Python", None # Asumimos Python por defecto para simplificar
            if "sobre" in mensaje_lower: tematica = mensaje_texto.split("sobre", 1)[1].strip()
            db.actualizar_usuario(numero_remitente, {"estado_conversacion": "eligiendo_dificultad", "tipo_reto_actual": tipo_reto, "tematica_actual": tematica})
            responder_mensaje(numero_remitente, "¿Qué nivel de dificultad prefieres? 🤔\n\n1. Fácil 🌱\n2. Intermedio 🔥\n3. Difícil 🤯", historial_chat)

        elif estado == "eligiendo_dificultad":
            dificultad = None
            if "1" in mensaje_texto or "fácil" in mensaje_lower: dificultad = "Fácil"
            elif "2" in mensaje_texto or "intermedio" in mensaje_lower: dificultad = "Intermedio"
            elif "3" in mensaje_texto or "difícil" in mensaje_lower: dificultad = "Difícil"
            
            if dificultad:
                tipo_reto = usuario["tipo_reto_actual"]
                tematica = usuario.get("tematica_actual")
                responder_mensaje(numero_remitente, f"¡Entendido! 👨‍💻 Buscando un reto de *{tipo_reto}* con dificultad *{dificultad}*...", historial_chat)
                reto = ai.generar_reto_con_ia(usuario['nivel'], tipo_reto, dificultad, tematica)
                if "error" in reto:
                    responder_mensaje(numero_remitente, reto["error"], historial_chat)
                    db.actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal"})
                else:
                    db.actualizar_usuario(numero_remitente, {"estado_conversacion": "resolviendo_reto", "reto_actual_enunciado": reto["enunciado"], "reto_actual_solucion": reto["solucion_ideal"], "reto_actual_pistas": json.dumps(reto["pistas"]), "pistas_usadas": 0})
                    responder_mensaje(numero_remitente, reto["enunciado"], historial_chat)
            else:
                responder_mensaje(numero_remitente, "Por favor, elige una dificultad: 1, 2 o 3.", historial_chat)

        elif mensaje_lower == "pista":
            if not usuario.get("reto_actual_enunciado"):
                responder_mensaje(numero_remitente, "No tienes un reto activo para pedir una pista.", historial_chat)
            else:
                pistas = json.loads(usuario.get("reto_actual_pistas", "[]"))
                pistas_usadas = usuario.get("pistas_usadas", 0)
                if pistas_usadas < len(pistas):
                    responder_mensaje(numero_remitente, f"🔍 *Pista {pistas_usadas + 1}/{len(pistas)}:* {pistas[pistas_usadas]}", historial_chat)
                    db.actualizar_usuario(numero_remitente, {"pistas_usadas": pistas_usadas + 1})
                else:
                    responder_mensaje(numero_remitente, "¡Ya has usado todas las pistas! 😥 Si quieres, puedes rendirte escribiendo `me rindo`.", historial_chat)
        
        elif mensaje_lower == "me rindo":
            if not usuario.get("reto_actual_solucion"):
                responder_mensaje(numero_remitente, "Tranquilo, no tienes ningún reto activo para rendirte. ¡Pide uno cuando quieras! 👍", historial_chat)
            else:
                solucion = usuario.get("reto_actual_solucion")
                mensaje_final = (f"¡No te preocupes! Rendirse es parte de aprender. Lo importante es entender cómo funciona. 💪\n\nAquí tienes la solución ideal:\n\n```\n{solucion}\n```\n\n¡Analízala y verás que la próxima vez lo conseguirás! Sigue practicando. ✨")
                db.actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal", "reto_actual_enunciado": None, "reto_actual_solucion": None, "curso_actual": None, "intentos_fallidos": 0})
                responder_mensaje(numero_remitente, mensaje_final, historial_chat)

        elif mensaje_lower == "mi perfil":
            manejar_seleccion_menu("ver_mi_perfil", numero_remitente, usuario)

        else:
            if estado in ["resolviendo_reto", "en_curso"]:
                feedback = ai.evaluar_solucion_con_ia(usuario["reto_actual_enunciado"], mensaje_texto, usuario["reto_actual_tipo"])
                
                if "[PREGUNTA]" in feedback:
                    tema_actual = CURSOS[usuario["curso_actual"]]["lecciones"][usuario["leccion_actual"]] if usuario.get("curso_actual") else "programación en general"
                    respuesta_conversacional = ai.chat_conversacional_con_ia(mensaje_texto, historial_chat, CURSOS, tema_actual)
                    responder_mensaje(numero_remitente, respuesta_conversacional, historial_chat)
                
                elif feedback.strip().upper().startswith("✅"):
                    db.actualizar_usuario(numero_remitente, {"intentos_fallidos": 0})
                    puntos_ganados = 10 * usuario["racha_dias"]
                    puntos_totales = usuario.get("puntos", 0) + puntos_ganados
                    nivel_actual = usuario["nivel"]
                    nuevo_nivel = (puntos_totales // 100) + 1
                    db.actualizar_usuario(numero_remitente, {"puntos": puntos_totales, "nivel": nuevo_nivel})
                    
                    mensaje_felicitacion = f"¡Ganaste *{puntos_ganados} puntos*! Tienes un total de {puntos_totales}."
                    if nuevo_nivel > nivel_actual:
                        mensaje_felicitacion += f"\n\n🚀 ¡FELICIDADES! ¡Has subido al Nivel {nuevo_nivel}!"
                    responder_mensaje(numero_remitente, mensaje_felicitacion, historial_chat)

                    if estado == "en_curso":
                        curso_key = usuario["curso_actual"]
                        leccion_actual_num = usuario["leccion_actual"] + 1
                        curso = CURSOS[curso_key]

                        if leccion_actual_num < len(curso["lecciones"]):
                            db.actualizar_usuario(numero_remitente, {"leccion_actual": leccion_actual_num})
                            tematica = curso['lecciones'][leccion_actual_num]
                            responder_mensaje(numero_remitente, f"¡Perfecto! ✅ Pasemos a la siguiente lección: **{tematica}**. Generando nuevo reto...", historial_chat)
                            
                            reto = ai.generar_reto_con_ia(usuario['nivel'], "Python", "Fácil", tematica)
                            if "error" in reto:
                                responder_mensaje(numero_remitente, reto["error"], historial_chat)
                            else:
                                db.actualizar_usuario(numero_remitente, {"reto_actual_enunciado": reto["enunciado"], "reto_actual_solucion": reto["solucion_ideal"], "reto_actual_pistas": json.dumps(reto["pistas"]), "pistas_usadas": 0})
                                responder_mensaje(numero_remitente, reto["enunciado"], historial_chat)
                        else:
                            responder_mensaje(numero_remitente, f"¡Felicidades! 🥳 ¡Has completado el curso *{curso['nombre']}*! Has demostrado una gran habilidad. ¿Listo para un reto aleatorio?", historial_chat)
                            db.actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal", "curso_actual": None})
                    else:
                        db.actualizar_usuario(numero_remitente, {"estado_conversacion": "menu_principal", "reto_actual_enunciado": None})

                else:
                    responder_mensaje(numero_remitente, feedback, historial_chat)
                    if estado == "en_curso":
                        intentos = usuario.get("intentos_fallidos", 0) + 1
                        db.actualizar_usuario(numero_remitente, {"intentos_fallidos": intentos})
                        if intentos >= UMBRAL_DE_FALLOS:
                            tema = CURSOS[usuario["curso_actual"]]["lecciones"][usuario["leccion_actual"]]
                            db.actualizar_usuario(numero_remitente, {"estado_conversacion": "esperando_ayuda_teorica"})
                            responder_mensaje(numero_remitente, f"Veo que este tema de **{tema}** se está complicando. ¿Quieres que te dé una explicación teórica sencilla antes de volver a intentarlo? (responde `sí` o `no`)", historial_chat)
            
            else:
                respuesta_chat = ai.chat_conversacional_con_ia(mensaje_texto, historial_chat, CURSOS)
                responder_mensaje(numero_remitente, respuesta_chat, historial_chat)

    except Exception as e:
        print(f"Ocurrió un error no manejado: {e}")
    return Response(status_code=200)

@app.on_event("startup")
async def startup_event():
    db.inicializar_db()

@app.get("/webhook")
async def verificar_webhook(request: Request):
    VERIFY_TOKEN = "micodigosecreto"
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode and token and mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, status_code=200)
    return Response(status_code=403)