# database.py

import sqlite3
import json
from datetime import date

# Cambiado a v3 para forzar la actualización del esquema en Render
DB_NAME = "logicbot_v3.db" 

def inicializar_db():
    """Crea la tabla de usuarios si no existe."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        numero_telefono TEXT PRIMARY KEY,
        nombre TEXT,
        nivel INTEGER DEFAULT 1,
        puntos INTEGER DEFAULT 0,
        racha_dias INTEGER DEFAULT 0,
        ultima_conexion TEXT,
        estado_conversacion TEXT,
        
        -- Columnas para el progreso del curso
        curso_actual TEXT,
        leccion_actual INTEGER DEFAULT 0,

        -- Columnas para los retos
        tematica_actual TEXT,
        tipo_reto_actual TEXT,
        reto_actual_enunciado TEXT,
        reto_actual_solucion TEXT,
        reto_actual_tipo TEXT,
        reto_actual_pistas TEXT,
        pistas_usadas INTEGER DEFAULT 0,
        historial_chat TEXT
    )
    """)
    conn.commit()
    conn.close()

def obtener_usuario(numero_telefono):
    """Obtiene los datos de un usuario por su número de teléfono."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE numero_telefono = ?", (numero_telefono,))
    usuario = cursor.fetchone()
    conn.close()
    return dict(usuario) if usuario else None

def crear_usuario(numero_telefono, nombre):
    """Crea un nuevo usuario en la base de datos."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    hoy = str(date.today())
    cursor.execute(
        "INSERT INTO usuarios (numero_telefono, nombre, estado_conversacion, ultima_conexion, historial_chat, racha_dias) VALUES (?, ?, ?, ?, ?, ?)",
        (numero_telefono, nombre, 'menu_principal', hoy, json.dumps([]), 1)
    )
    conn.commit()
    conn.close()

def actualizar_usuario(numero_telefono, datos):
    """Actualiza uno o más campos de un usuario."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    campos = ", ".join([f"{key} = ?" for key in datos.keys()])
    valores = list(datos.values())
    valores.append(numero_telefono)
    cursor.execute(f"UPDATE usuarios SET {campos} WHERE numero_telefono = ?", tuple(valores))
    conn.commit()
    conn.close()