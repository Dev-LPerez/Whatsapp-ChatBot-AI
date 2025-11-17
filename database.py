# database.py

import os
import json
import time
import random
from datetime import date
from sqlalchemy import create_engine, Column, String, Integer, Text, update, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, ProgrammingError
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

    # Nuevos campos (Onboarding y Logros)
    onboarding_completado = Column(Integer, default=0)
    preferencia_aprendizaje = Column(String, nullable=True)
    nivel_inicial = Column(String, nullable=True)
    logros_desbloqueados = Column(Text, default='[]')
    retos_completados = Column(Integer, default=0)
    retos_sin_pistas = Column(Integer, default=0)


# --- FUNCIONES AUXILIARES ---

def inicializar_db():
    """
    Inicializa la DB y realiza migraciones automáticas.
    Maneja la concurrencia de múltiples workers con retardos y manejo de errores.
    """
    # Pequeña pausa aleatoria para desincronizar los workers y reducir choques
    time.sleep(random.uniform(0.1, 0.5))

    print("🔍 Verificando esquema de base de datos...")

    try:
        # Usamos un inspector fresco
        inspector = inspect(engine)

        # 1. CREACIÓN DE TABLA
        if not inspector.has_table("usuarios"):
            print("🆕 Intentando crear tabla 'usuarios'...")
            try:
                Base.metadata.create_all(bind=engine)
                print("✅ Tabla 'usuarios' creada exitosamente.")
            except (IntegrityError, ProgrammingError) as e:
                # Si falla porque ya existe (race condition), lo ignoramos
                if "already exists" in str(e) or "duplicate key" in str(e):
                    print("⚠️ La tabla fue creada por otro worker concurrentemente. Continuando...")
                else:
                    print(f"❌ Error crítico creando tabla: {e}")
        else:
            print("ℹ️ La tabla 'usuarios' ya existe.")

        # 2. MIGRACIÓN DE COLUMNAS (Auto-migration)
        # Lista de columnas requeridas y sus tipos
        nuevas_columnas = {
            "onboarding_completado": "INTEGER DEFAULT 0",
            "preferencia_aprendizaje": "VARCHAR",
            "nivel_inicial": "VARCHAR",
            "logros_desbloqueados": "TEXT DEFAULT '[]'",
            "retos_completados": "INTEGER DEFAULT 0",
            "retos_sin_pistas": "INTEGER DEFAULT 0"
        }

        # Refrescamos el inspector para ver columnas actuales
        inspector = inspect(engine)
        columnas_existentes = [col['name'] for col in inspector.get_columns("usuarios")]

        with engine.connect() as conn:
            trans = conn.begin()
            try:
                cambios_realizados = False
                for col_nombre, col_def in nuevas_columnas.items():
                    if col_nombre not in columnas_existentes:
                        print(f"🛠️ Migrando: Añadiendo columna '{col_nombre}'...")
                        try:
                            conn.execute(text(f"ALTER TABLE usuarios ADD COLUMN {col_nombre} {col_def}"))
                            cambios_realizados = True
                        except Exception as e:
                            # Ignoramos si la columna ya fue creada por otro worker
                            print(f"⚠️ Aviso migración '{col_nombre}': {e}")

                trans.commit()
                if cambios_realizados:
                    print("✅ Migración de base de datos completada.")
                else:
                    print("✅ Esquema de base de datos al día.")
            except Exception as e:
                trans.rollback()
                print(f"❌ Error durante la migración automática: {e}")

    except Exception as e:
        print(f"⚠️ Error general en inicialización (no bloqueante): {e}")


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
    with get_db_session() as db:
        usuario = db.query(Usuario).filter(Usuario.numero_telefono == str(numero_telefono)).first()
        if usuario:
            return {c.name: getattr(usuario, c.name) for c in usuario.__table__.columns}
    return None


def crear_usuario(numero_telefono, nombre):
    # Doble verificación rápida
    if obtener_usuario(numero_telefono):
        return

    progreso_inicial = {}
    java_lessons = CURSOS.get("java", {}).get("lecciones", [])
    for leccion in java_lessons:
        progreso_inicial[leccion] = {"puntos": 0, "nivel": 1}

    try:
        with get_db_session() as db:
            nuevo_usuario = Usuario(
                numero_telefono=str(numero_telefono),
                nombre=nombre,
                racha_dias=1,
                progreso_temas=json.dumps(progreso_inicial)
            )
            db.add(nuevo_usuario)
            db.commit()
            print(f"✅ Usuario {numero_telefono} creado y GUARDADO exitosamente")
    except IntegrityError:
        # Si da error de integridad es porque ya existe (race condition), lo ignoramos
        print(f"ℹ️ Usuario {numero_telefono} ya existía (concurrencia).")
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")


def actualizar_usuario(numero_telefono, datos):
    try:
        with get_db_session() as db:
            stmt = update(Usuario).where(Usuario.numero_telefono == str(numero_telefono)).values(**datos)
            db.execute(stmt)
            db.commit()
    except Exception as e:
        print(f"❌ Error al actualizar usuario: {e}")