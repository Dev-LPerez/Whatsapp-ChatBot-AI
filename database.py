# database.py (versión para PostgreSQL - con progreso por temas)

import os
import json
from datetime import date
from sqlalchemy import create_engine, Column, String, Integer, Text, update, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from config import CURSOS # Importamos CURSOS para la inicialización

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"

    numero_telefono = Column(String, primary_key=True, index=True)
    nombre = Column(String)
    # Nivel y puntos generales
    nivel = Column(Integer, default=1)
    puntos = Column(Integer, default=0)
    racha_dias = Column(Integer, default=0)
    ultima_conexion = Column(String, default=lambda: str(date.today()))
    estado_conversacion = Column(String, default='menu_principal')
    curso_actual = Column(String, nullable=True)
    leccion_actual = Column(Integer, default=0)
    intentos_fallidos = Column(Integer, default=0)
    # Novedad: Almacenará la temática actual del reto para actualizar el progreso correcto
    tematica_actual = Column(String, nullable=True) 
    tipo_reto_actual = Column(String, nullable=True)
    dificultad_reto_actual = Column(String, nullable=True)
    reto_actual_enunciado = Column(Text, nullable=True)
    reto_actual_solucion = Column(Text, nullable=True)
    reto_actual_pistas = Column(Text, nullable=True)
    pistas_usadas = Column(Integer, default=0)
    historial_chat = Column(Text, default='[]')
    # NUEVA COLUMNA: Almacena un JSON con el progreso por tema
    progreso_temas = Column(Text, default='{}')

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
    finally:
        db.close()

def obtener_usuario(numero_telefono):
    with get_db_session() as db:
        usuario = db.query(Usuario).filter(Usuario.numero_telefono == numero_telefono).first()
        if usuario:
            return {c.name: getattr(usuario, c.name) for c in usuario.__table__.columns}
    return None

def crear_usuario(numero_telefono, nombre):
    """
    Crea un nuevo usuario en la base de datos con progreso inicial.
    """
    # Inicializamos el progreso del tema para el curso de Java
    progreso_inicial = {}
    java_lessons = CURSOS.get("java", {}).get("lecciones", [])
    for leccion in java_lessons:
        progreso_inicial[leccion] = {"puntos": 0, "nivel": 1}

    with get_db_session() as db:
        nuevo_usuario = Usuario(
            numero_telefono=numero_telefono,
            nombre=nombre,
            racha_dias=1,
            progreso_temas=json.dumps(progreso_inicial)
        )
        db.add(nuevo_usuario)
        # El commit se hace automáticamente en get_db_session

def actualizar_usuario(numero_telefono, datos):
    with get_db_session() as db:
        stmt = update(Usuario).where(Usuario.numero_telefono == numero_telefono).values(**datos)
        db.execute(stmt)
        db.commit()