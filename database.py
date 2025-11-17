# database.py

import os
import json
from datetime import date
from sqlalchemy import create_engine, Column, String, Integer, Text, update, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from config import CURSOS

DATABASE_URL = os.getenv("DATABASE_URL")

# Configuración de SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODELO DE USUARIO ---
class Usuario(Base):
    __tablename__ = "usuarios"

    numero_telefono = Column(String, primary_key=True, index=True)
    nombre = Column(String)
    nivel = Column(Integer, default=1)
    puntos = Column(Integer, default=0)
    racha_dias = Column(Integer, default=0)
    ultima_conexion = Column(String, default=lambda: str(date.today()))
    estado_conversacion = Column(String, default='menu_principal')
    curso_actual = Column(String, nullable=True)
    leccion_actual = Column(Integer, default=0)
    intentos_fallidos = Column(Integer, default=0)
    tematica_actual = Column(String, nullable=True)
    tipo_reto_actual = Column(String, nullable=True)
    dificultad_reto_actual = Column(String, nullable=True)
    reto_actual_enunciado = Column(Text, nullable=True)
    reto_actual_solucion = Column(Text, nullable=True)
    reto_actual_pistas = Column(Text, nullable=True)
    pistas_usadas = Column(Integer, default=0)
    historial_chat = Column(Text, default='[]')
    progreso_temas = Column(Text, default='{}')

# --- FUNCIONES AUXILIARES ---

def inicializar_db():
    print("Verificando la base de datos...")
    inspector = inspect(engine)
    if not inspector.has_table("usuarios"):
        print("La tabla 'usuarios' no existe. Creando todas las tablas...")
        Base.metadata.create_all(bind=engine)
        print("Tablas creadas exitosamente.")
    else:
        print("Las tablas ya existen. No se requiere ninguna acción.")

@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"⚠️ Error en sesión de DB, haciendo rollback: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def obtener_usuario(numero_telefono):
    # Imprimir log para depuración
    print(f"🔍 Buscando usuario: '{numero_telefono}' (Tipo: {type(numero_telefono)})")
    with get_db_session() as db:
        # Buscamos asegurando que sea string
        usuario = db.query(Usuario).filter(Usuario.numero_telefono == str(numero_telefono)).first()
        if usuario:
            print("✅ Usuario encontrado en DB")
            # Convertimos a diccionario para evitar problemas al cerrar la sesión
            return {c.name: getattr(usuario, c.name) for c in usuario.__table__.columns}
        else:
            print("❌ Usuario NO encontrado en DB")
    return None

def crear_usuario(numero_telefono, nombre):
    # Doble verificación para evitar condiciones de carrera
    if obtener_usuario(numero_telefono):
        return

    progreso_inicial = {}
    java_lessons = CURSOS.get("java", {}).get("lecciones", [])
    for leccion in java_lessons:
        progreso_inicial[leccion] = {"puntos": 0, "nivel": 1}

    try:
        with get_db_session() as db:
            nuevo_usuario = Usuario(
                numero_telefono=str(numero_telefono), # Aseguramos string
                nombre=nombre,
                racha_dias=1,
                progreso_temas=json.dumps(progreso_inicial)
            )
            db.add(nuevo_usuario)
            db.commit() # <--- ¡ESTA LÍNEA ES LA CLAVE! GUARDAR CAMBIOS
            print(f"✅ Usuario {numero_telefono} creado y GUARDADO exitosamente")
    except Exception as e:
        print(f"❌ Error CRÍTICO al crear usuario: {e}")

def actualizar_usuario(numero_telefono, datos):
    try:
        with get_db_session() as db:
            stmt = update(Usuario).where(Usuario.numero_telefono == str(numero_telefono)).values(**datos)
            db.execute(stmt)
            db.commit() # <--- ¡ESTA LÍNEA ES LA CLAVE! GUARDAR CAMBIOS
    except Exception as e:
        print(f"❌ Error al actualizar usuario: {e}")