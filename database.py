# database.py (Versión Firebase Firestore)

import os
import json
from datetime import date, datetime
import firebase_admin
from firebase_admin import credentials, firestore
from config import CURSOS

# --- CONFIGURACIÓN DE FIREBASE ---

CREDENTIALS_FILE = "firebase_credentials.json"

if not firebase_admin._apps:
    try:
        if os.path.exists(CREDENTIALS_FILE):
            cred = credentials.Certificate(CREDENTIALS_FILE)
            firebase_admin.initialize_app(cred)
            print("🔥 Firebase inicializado con archivo local.")
        else:
            print("⚠️ No se encontró firebase_credentials.json. Intentando credenciales por defecto...")
            firebase_admin.initialize_app()
            print("🔥 Firebase inicializado (Default Credentials).")
    except Exception as e:
        print(f"❌ Error inicializando Firebase: {e}")

try:
    db = firestore.client()
except Exception:
    db = None
    print("❌ No se pudo conectar a Firestore. Verifica las credenciales.")

COLLECTION_USERS = "usuarios"
# ID de la app para sincronización con el Dashboard Web
# Debe coincidir con el usado en el frontend React
APP_ID_DASHBOARD = "default-logicbot"


# --- FUNCIONES DE BASE DE DATOS ---

def inicializar_db():
    if db:
        print("✅ Conexión a Firestore activa.")
    else:
        print("❌ Error: Firestore no está conectado.")


def obtener_usuario(numero_telefono):
    if not db: return None
    try:
        doc_ref = db.collection(COLLECTION_USERS).document(str(numero_telefono))
        doc = doc_ref.get()
        if doc.exists:
            datos = doc.to_dict()
            datos['numero_telefono'] = str(numero_telefono)
            return datos
        else:
            return None
    except Exception as e:
        print(f"Error obteniendo usuario: {e}")
        return None


def crear_usuario(numero_telefono, nombre):
    if not db: return
    if obtener_usuario(numero_telefono): return

    progreso_inicial = {}
    java_lessons = CURSOS.get("java", {}).get("lecciones", [])
    for leccion in java_lessons:
        progreso_inicial[leccion] = {"puntos": 0, "nivel": 1}

    nuevo_usuario = {
        "numero_telefono": str(numero_telefono),
        "nombre": nombre,
        "nivel": 1,
        "puntos": 0,
        "racha_dias": 1,
        "ultima_conexion": str(date.today()),
        "estado_conversacion": "menu_principal",
        "curso_actual": None,
        "leccion_actual": 0,
        "intentos_fallidos": 0,
        "tematica_actual": None,
        "tipo_reto_actual": None,
        "dificultad_reto_actual": None,
        "reto_actual_enunciado": None,
        "reto_actual_solucion": None,
        "reto_actual_pistas": None,
        "pistas_usadas": 0,
        "historial_chat": "[]",
        "progreso_temas": json.dumps(progreso_inicial),
        "onboarding_completado": 0,
        "preferencia_aprendizaje": None,
        "nivel_inicial": None,
        "logros_desbloqueados": "[]",
        "retos_completados": 0,
        "retos_sin_pistas": 0,
        "class_token": None,  # Campo nuevo para vinculación
        # NUEVOS CAMPOS GLOBALES PARA ANALÍTICA
        "total_pistas_usadas": 0,  # Histórico acumulado
        "total_fallos": 0  # Histórico de errores
    }

    try:
        db.collection(COLLECTION_USERS).document(str(numero_telefono)).set(nuevo_usuario)
        print(f"✅ Usuario {numero_telefono} creado en Firestore exitosamente")
        # Sincronizar creación con el dashboard
        sincronizar_con_dashboard(str(numero_telefono), nuevo_usuario)
    except Exception as e:
        print(f"❌ Error al crear usuario en Firestore: {e}")


def actualizar_usuario(numero_telefono, datos):
    if not db: return
    try:
        doc_ref = db.collection(COLLECTION_USERS).document(str(numero_telefono))
        doc_ref.update(datos)

        # Sincronización automática con Dashboard si hay cambios relevantes
        campos_dashboard = ["puntos", "nivel", "racha_dias", "progreso_temas", "retos_completados", "historial_chat",
                            "class_token", "total_pistas_usadas", "total_fallos"]
        if any(campo in datos for campo in campos_dashboard):
            # Obtenemos el usuario completo actualizado para sincronizar
            usuario_actualizado = obtener_usuario(numero_telefono)
            if usuario_actualizado:
                sincronizar_con_dashboard(numero_telefono, usuario_actualizado)

    except Exception as e:
        print(f"❌ Error al actualizar usuario: {e}")


def sincronizar_con_dashboard(numero_telefono, datos_usuario):
    """
    Copia los datos esenciales a la colección pública 'artifacts'
    para que el Dashboard Web pueda leerlos.
    """
    if not db: return

    # Preparamos solo los datos que el dashboard necesita ver
    datos_publicos = {
        "nombre": datos_usuario.get("nombre"),
        "numero_telefono": str(numero_telefono),
        "class_token": datos_usuario.get("class_token"),
        "nivel": datos_usuario.get("nivel"),
        "puntos": datos_usuario.get("puntos"),
        "racha_dias": datos_usuario.get("racha_dias"),
        "progreso_temas": datos_usuario.get("progreso_temas"),
        "retos_completados": datos_usuario.get("retos_completados"),
        "retos_sin_pistas": datos_usuario.get("retos_sin_pistas"),
        "pistas_usadas": datos_usuario.get("pistas_usadas"),
        "ultima_conexion": datos_usuario.get("ultima_conexion"),
        # NUEVOS CAMPOS PARA ANALÍTICA
        "total_pistas_usadas": datos_usuario.get("total_pistas_usadas", 0),
        "total_fallos": datos_usuario.get("total_fallos", 0),
        # Limitamos el historial para no saturar
        "historial_chat": datos_usuario.get("historial_chat", "[]")
    }

    try:
        # Ruta: artifacts/{APP_ID}/public/data/users_sync/{numero_telefono}
        # Esta ruta es legible por el frontend
        (db.collection('artifacts').document(APP_ID_DASHBOARD)
         .collection('public').document('data')
         .collection('users_sync').document(str(numero_telefono))
         .set(datos_publicos))
    except Exception as e:
        print(f"⚠️ Error sincronizando con dashboard: {e}")


def vincular_alumno_a_clase(numero_telefono, token_clase):
    """Vincula un alumno a una clase específica mediante token."""
    if not db: return False

    print(f"🔗 Vinculando {numero_telefono} a clase {token_clase}")
    try:
        # 1. Actualizar registro principal
        actualizar_usuario(numero_telefono, {"class_token": token_clase})
        return True
    except Exception as e:
        print(f"❌ Error vinculando clase: {e}")
        return False


# ✅ NUEVA FUNCIÓN PARA REGISTRAR ALERTAS
def registrar_alerta_seguridad(numero_telefono, datos_alerta):
    """
    Registra una alerta de integridad (velocidad, copy-paste) en Firestore
    para que sea notificada en el Dashboard Docente.
    """
    if not db: return False

    try:
        # Estructura del documento de alerta
        alerta = {
            "tipo": "velocidad_sospechosa",
            "nivel_severidad": "alta",  # alta, media, baja
            "estudiante_id": str(numero_telefono),
            "nombre_estudiante": datos_alerta.get("nombre", "Estudiante"),

            # Detalles del evento
            "reto_enunciado": datos_alerta.get("enunciado"),
            "respuesta_estudiante": datos_alerta.get("respuesta"),

            # Evidencia temporal
            "tiempo_estimado": datos_alerta.get("tiempo_estimado"),
            "tiempo_tomado": datos_alerta.get("tiempo_tomado"),
            "timestamp_envio": datos_alerta.get("timestamp_envio"),  # ✅ Hora del envío del reto
            "timestamp_alerta": datetime.now().isoformat(),  # ✅ Hora de detección de la alerta

            # Metadatos
            "leida": False,
            "creado_en": datetime.now().isoformat()
        }

        # Guardamos en la colección pública 'alerts' dentro de artifacts
        # Ruta: artifacts/{APP_ID}/public/data/alerts/{auto_id}
        (db.collection('artifacts').document(APP_ID_DASHBOARD)
         .collection('public').document('data')
         .collection('alerts').add(alerta))

        print(f"🚨 Alerta de seguridad registrada para {numero_telefono}")
        return True

    except Exception as e:
        print(f"❌ Error registrando alerta en BD: {e}")
        return False
