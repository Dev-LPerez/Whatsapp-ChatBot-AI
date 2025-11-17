# database.py (Versión Firebase Firestore)

import os
import json
from datetime import date
import firebase_admin
from firebase_admin import credentials, firestore
from config import CURSOS

# --- CONFIGURACIÓN DE FIREBASE ---

# Nombre del archivo de credenciales (debe estar en la raíz o configurado en Render)
CREDENTIALS_FILE = "firebase_credentials.json"

# Inicializar la app de Firebase una sola vez
if not firebase_admin._apps:
    try:
        # Intenta leer del archivo JSON local (Desarrollo)
        if os.path.exists(CREDENTIALS_FILE):
            cred = credentials.Certificate(CREDENTIALS_FILE)
            firebase_admin.initialize_app(cred)
            print("🔥 Firebase inicializado con archivo local.")
        else:
            # Si no hay archivo, intentamos usar las credenciales por defecto de Google Cloud (Producción)
            # O lanzamos un aviso si no está configurado
            print("⚠️ No se encontró firebase_credentials.json. Intentando credenciales por defecto...")
            firebase_admin.initialize_app()
            print("🔥 Firebase inicializado (Default Credentials).")
    except Exception as e:
        print(f"❌ Error inicializando Firebase: {e}")

# Obtener cliente de Firestore
try:
    db = firestore.client()
except Exception:
    db = None
    print("❌ No se pudo conectar a Firestore. Verifica las credenciales.")

# Nombre de la colección (equivalente a Tabla)
COLLECTION_USERS = "usuarios"


# --- FUNCIONES DE BASE DE DATOS ---

def inicializar_db():
    """
    En Firebase no hace falta crear tablas.
    Solo verificamos la conexión.
    """
    if db:
        print("✅ Conexión a Firestore activa.")
    else:
        print("❌ Error: Firestore no está conectado.")


def obtener_usuario(numero_telefono):
    """Obtiene los datos de un usuario por su número de teléfono (ID del documento)."""
    if not db: return None

    try:
        doc_ref = db.collection(COLLECTION_USERS).document(str(numero_telefono))
        doc = doc_ref.get()

        if doc.exists:
            datos = doc.to_dict()
            # Aseguramos que el número esté en los datos (aunque sea el ID)
            datos['numero_telefono'] = str(numero_telefono)
            return datos
        else:
            return None
    except Exception as e:
        print(f"Error obteniendo usuario: {e}")
        return None


def crear_usuario(numero_telefono, nombre):
    """Crea un nuevo documento de usuario en Firestore."""
    if not db: return

    # Verificar si ya existe para no sobrescribir (opcional en Firestore, pero buena práctica)
    if obtener_usuario(numero_telefono):
        return

    # Progreso inicial
    progreso_inicial = {}
    java_lessons = CURSOS.get("java", {}).get("lecciones", [])
    for leccion in java_lessons:
        progreso_inicial[leccion] = {"puntos": 0, "nivel": 1}

    # Estructura del documento (JSON)
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
        "historial_chat": "[]",  # Guardamos como string JSON por compatibilidad
        "progreso_temas": json.dumps(progreso_inicial),
        # Campos nuevos UX
        "onboarding_completado": 0,
        "preferencia_aprendizaje": None,
        "nivel_inicial": None,
        "logros_desbloqueados": "[]",
        "retos_completados": 0,
        "retos_sin_pistas": 0
    }

    try:
        # .set() crea o sobrescribe el documento con el ID específico
        db.collection(COLLECTION_USERS).document(str(numero_telefono)).set(nuevo_usuario)
        print(f"✅ Usuario {numero_telefono} creado en Firestore exitosamente")
    except Exception as e:
        print(f"❌ Error al crear usuario en Firestore: {e}")


def actualizar_usuario(numero_telefono, datos):
    """Actualiza campos específicos de un usuario."""
    if not db: return

    try:
        doc_ref = db.collection(COLLECTION_USERS).document(str(numero_telefono))
        # .update() solo cambia los campos que le pases
        doc_ref.update(datos)
    except Exception as e:
        print(f"❌ Error al actualizar usuario: {e}")