"""
Script de prueba para verificar la configuración del proyecto
"""
import os
import sys
from pathlib import Path

def verificar_python():
    """Verifica la versión de Python"""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("⚠️  ADVERTENCIA: Se recomienda Python 3.11 o superior")
        return False
    return True

def verificar_archivo(ruta, nombre):
    """Verifica si existe un archivo"""
    if Path(ruta).exists():
        print(f"✓ {nombre} encontrado")
        return True
    else:
        print(f"✗ {nombre} NO encontrado")
        return False

def verificar_env():
    """Verifica variables de entorno críticas"""
    vars_criticas = [
        "DATABASE_URL",
        "WHATSAPP_TOKEN",
        "ID_NUMERO_TELEFONO",
        "GEMINI_API_KEY",
        "VERIFY_TOKEN"
    ]

    print("\n📋 Variables de Entorno:")
    faltantes = []
    for var in vars_criticas:
        valor = os.getenv(var)
        if valor:
            # Ocultar parte del valor por seguridad
            valor_oculto = valor[:8] + "..." if len(valor) > 8 else "***"
            print(f"✓ {var} = {valor_oculto}")
        else:
            print(f"✗ {var} = NO CONFIGURADA")
            faltantes.append(var)

    return len(faltantes) == 0, faltantes

def verificar_importaciones():
    """Verifica que las librerías principales se puedan importar"""
    print("\n📦 Librerías:")
    libs = {
        "fastapi": "FastAPI",
        "firebase_admin": "Firebase Admin SDK",
        "requests": "Requests",
        "google.generativeai": "Google Gemini AI",
        "uvicorn": "Uvicorn",
        "gunicorn": "Gunicorn"
    }

    todas_ok = True
    for lib, nombre in libs.items():
        try:
            __import__(lib)
            print(f"✓ {nombre}")
        except ImportError:
            print(f"✗ {nombre} - NO INSTALADA")
            todas_ok = False

    return todas_ok

def main():
    print("=" * 60)
    print("🤖 LogicBot - Verificación de Configuración")
    print("=" * 60)

    # Verificar Python
    print("\n🐍 Versión de Python:")
    py_ok = verificar_python()

    # Verificar archivos
    print("\n📁 Archivos del Proyecto:")
    archivos_obligatorios = [
        ("src/main.py", "src/main.py"),
        ("src/database.py", "src/database.py"),
        ("src/message_handler.py", "src/message_handler.py"),
        ("src/ai_services.py", "src/ai_services.py"),
        ("src/whatsapp_utils.py", "src/whatsapp_utils.py"),
        ("src/config/config.py", "src/config/config.py"),
        ("requirements.txt", "requirements.txt"),
        ("Procfile", "Procfile (Deployment)")
    ]

    archivos_opcionales = [
        (".env", ".env (Variables de Entorno - Opcional)")
    ]

    archivos_ok = all(verificar_archivo(ruta, nombre) for ruta, nombre in archivos_obligatorios)

    # Verificar opcionales sin afectar el resultado
    for ruta, nombre in archivos_opcionales:
        verificar_archivo(ruta, nombre)

    # Verificar variables de entorno
    env_ok, faltantes = verificar_env()

    # Verificar librerías (solo si hay .venv activado)
    libs_ok = verificar_importaciones()

    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)

    resultados = [
        ("Python 3.11+", py_ok),
        ("Archivos del proyecto", archivos_ok),
        ("Variables de entorno", env_ok),
        ("Librerías instaladas", libs_ok)
    ]

    for item, estado in resultados:
        icono = "✅" if estado else "❌"
        print(f"{icono} {item}")

    # Próximos pasos
    print("\n" + "=" * 60)
    print("🚀 PRÓXIMOS PASOS")
    print("=" * 60)

    if not env_ok:
        print("\n1. Configurar variables de entorno:")
        print("   - Copia .env.example como .env")
        print("   - Completa con tus valores reales:")
        for var in faltantes:
            print(f"     * {var}")

    if not libs_ok:
        print("\n2. Instalar dependencias:")
        print("   pip install -r requirements.txt")

    if archivos_ok and env_ok and libs_ok:
        print("\n✅ ¡Todo está listo!")
        print("\n3. Iniciar el servidor:")
        print("   uvicorn main:app --reload")
        print("\n4. El webhook estará disponible en:")
        print("   http://localhost:8000/webhook")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    # Cargar variables de entorno si existe .env
    try:
        from dotenv import load_dotenv
        if Path(".env").exists():
            load_dotenv()
    except ImportError:
        pass

    main()

