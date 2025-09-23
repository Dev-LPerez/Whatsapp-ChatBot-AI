# database.py (versión para PostgreSQL)

import os
import json
from datetime import date
from sqlalchemy import create_engine, Column, String, Integer, Text, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

# La URL se leerá desde una variable de entorno segura en Render
DATABASE_URL = os.getenv("DATABASE_URL")

# --- CONFIGURACIÓN DE LA CONEXIÓN ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODELO DE LA TABLA (la definición de nuestro usuario) ---
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

# --- FUNCIÓN PARA CREAR LA TABLA SI NO EXISTE ---
def inicializar_db():
    Base.metadata.create_all(bind=engine, checkfirst=True)

@contextmanager
def get_db_session():
    """Manejador de sesión para asegurar que la conexión se cierre siempre."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- FUNCIONES PARA INTERACTUAR CON LA BASE DE DATOS ---

def obtener_usuario(numero_telefono):
    with get_db_session() as db:
        usuario = db.query(Usuario).filter(Usuario.numero_telefono == numero_telefono).first()
        if usuario:
            return {c.name: getattr(usuario, c.name) for c in usuario.__table__.columns}
    return None

def crear_usuario(numero_telefono, nombre):
    with get_db_session() as db:
        nuevo_usuario = Usuario(
            numero_telefono=numero_telefono,
            nombre=nombre,
            racha_dias=1
        )
        db.add(nuevo_usuario)
        db.commit()

def actualizar_usuario(numero_telefono, datos):
    with get_db_session() as db:
        stmt = update(Usuario).where(Usuario.numero_telefono == numero_telefono).values(**datos)
        db.execute(stmt)
        db.commit()