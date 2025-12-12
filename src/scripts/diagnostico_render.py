#!/usr/bin/env python3
"""
Script de diagnóstico completo para Render.
Verifica configuración, conexiones y estado del servicio.

USO:
    python diagnostico_render.py
"""

import os
import sys
import json
from datetime import datetime

def print_header(title):
    """Imprime un encabezado formateado."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_env_vars():
    """Verifica que todas las variables de entorno estén configuradas."""
    print_header("🔍 VERIFICACIÓN DE VARIABLES DE ENTORNO")

    required_vars = {
        "DATABASE_URL": "Conexión a PostgreSQL",
        "WHATSAPP_TOKEN": "Token de WhatsApp Business API",
        "ID_NUMERO_TELEFONO": "ID del número de WhatsApp",
        "GEMINI_API_KEY": "API Key de Google Gemini",
        "VERIFY_TOKEN": "Token de verificación del webhook"
    }

    all_ok = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Ocultar parte del valor por seguridad
            masked = value[:10] + "..." if len(value) > 10 else "***"
            print(f"✅ {var:25} {masked:20} ({description})")
        else:
            print(f"❌ {var:25} {'NO CONFIGURADA':20} ({description})")
            all_ok = False

    return all_ok

def check_database():
    """Verifica la conexión a la base de datos."""
    print_header("💾 VERIFICACIÓN DE BASE DE DATOS")

    try:
        import database as db

        # Intentar conectar
        print("📡 Intentando conectar a PostgreSQL...")
        db.inicializar_db()
        print("✅ Conexión a la base de datos exitosa")

        # Verificar si hay usuarios
        try:
            test_user = db.obtener_usuario("test_diagnostico")
            if test_user is None:
                print("📊 Base de datos lista (sin usuarios de prueba)")
            else:
                print("📊 Base de datos con datos existentes")
        except Exception as e:
            print(f"⚠️  Advertencia al consultar: {e}")

        return True

    except Exception as e:
        print(f"❌ Error al conectar con la base de datos:")
        print(f"   {str(e)}")
        return False

def check_imports():
    """Verifica que todas las librerías necesarias estén instaladas."""
    print_header("📦 VERIFICACIÓN DE LIBRERÍAS")

    libraries = {
        "fastapi": "FastAPI (Framework web)",
        "uvicorn": "Uvicorn (Servidor ASGI)",
        "sqlalchemy": "SQLAlchemy (ORM)",
        "psycopg2": "psycopg2 (Driver PostgreSQL)",
        "requests": "Requests (HTTP client)",
        "google.genai": "Google Gemini AI",
        "pydantic": "Pydantic (Validación)"
    }

    all_ok = True
    for lib, description in libraries.items():
        try:
            __import__(lib)
            print(f"✅ {lib:20} {description}")
        except ImportError:
            print(f"❌ {lib:20} NO INSTALADA - {description}")
            all_ok = False

    return all_ok

def check_files():
    """Verifica que todos los archivos necesarios existan."""
    print_header("📁 VERIFICACIÓN DE ARCHIVOS")

    required_files = {
        "main.py": "Archivo principal (FastAPI)",
        "database.py": "Gestión de base de datos",
        "message_handler.py": "Lógica de mensajes",
        "ai_services.py": "Servicios de IA",
        "whatsapp_utils.py": "Utilidades de WhatsApp",
        "config.py": "Configuración",
        "requirements.txt": "Dependencias",
        "Procfile": "Configuración de Render"
    }

    all_ok = True
    for file, description in required_files.items():
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file:25} {size:8} bytes - {description}")
        else:
            print(f"❌ {file:25} {'NO ENCONTRADO':15} - {description}")
            all_ok = False

    return all_ok

def check_render_specific():
    """Verifica configuraciones específicas de Render."""
    print_header("🚀 VERIFICACIÓN DE CONFIGURACIÓN RENDER")

    # Verificar si estamos en Render
    is_render = os.getenv('RENDER') is not None
    print(f"🌍 Entorno detectado: {'Render (Producción)' if is_render else 'Local (Desarrollo)'}")

    # Puerto
    port = os.getenv('PORT', '8000')
    print(f"🔌 Puerto configurado: {port}")

    # Verificar Procfile
    if os.path.exists('Procfile'):
        with open('Procfile', 'r') as f:
            procfile_content = f.read().strip()
            print(f"📋 Procfile: {procfile_content}")

            if 'gunicorn' in procfile_content and 'uvicorn' in procfile_content:
                print("✅ Procfile correctamente configurado")
            else:
                print("⚠️  Procfile puede tener problemas")

    return True

def generate_report():
    """Genera un reporte completo del estado."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "DIAGNÓSTICO COMPLETO - LogicBot" + " " * 21 + "║")
    print("╚" + "═" * 68 + "╝")

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n📅 Fecha/Hora: {timestamp}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"💻 Sistema: {sys.platform}")

    # Ejecutar todas las verificaciones
    results = {
        "Variables de entorno": check_env_vars(),
        "Archivos del proyecto": check_files(),
        "Librerías instaladas": check_imports(),
        "Base de datos": check_database(),
        "Configuración Render": check_render_specific()
    }

    # Resumen final
    print_header("📊 RESUMEN DEL DIAGNÓSTICO")

    all_passed = True
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10} {check}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ¡TODOS LOS CHECKS PASARON! El proyecto está listo para Render.")
    else:
        print("⚠️  Algunos checks fallaron. Revisa los detalles arriba.")
    print("=" * 70)

    return all_passed

def main():
    """Función principal."""
    try:
        result = generate_report()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Diagnóstico interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado durante el diagnóstico:")
        print(f"   {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

