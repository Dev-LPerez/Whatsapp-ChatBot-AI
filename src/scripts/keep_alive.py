"""
Script para mantener el servicio de Render despierto.
Ejecuta pings cada 14 minutos para evitar que el servicio gratuito se suspenda.

USO:
    python keep_alive.py https://chatbot-ai-logica-de-programacion.onrender.com
"""

import requests
import time
import sys
from datetime import datetime

def ping_service(url):
    """
    Hace un ping al servicio para mantenerlo despierto.
    """
    try:
        # Ping al endpoint de health check
        health_url = f"{url.rstrip('/')}/health"
        response = requests.get(health_url, timeout=30)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if response.status_code == 200:
            data = response.json()
            print(f"[{timestamp}] ✅ Ping exitoso - Status: {data.get('status')}")
            return True
        else:
            print(f"[{timestamp}] ⚠️  Ping respondió con código: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] ⏱️  Timeout - El servicio puede estar despertando (cold start)")
        return False
    except requests.exceptions.RequestException as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] ❌ Error al hacer ping: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("❌ Error: Debes proporcionar la URL del servicio")
        print("Uso: python keep_alive.py https://chatbot-ai-logica-de-programacion.onrender.com")
        sys.exit(1)

    service_url = sys.argv[1]
    ping_interval = 14 * 60  # 14 minutos en segundos (Render suspende después de 15 min)

    print("=" * 70)
    print("🤖 LogicBot - Keep Alive Service")
    print("=" * 70)
    print(f"🎯 Servicio objetivo: {service_url}")
    print(f"⏰ Intervalo de ping: {ping_interval // 60} minutos")
    print(f"🚀 Iniciando monitoreo...")
    print("=" * 70)
    print()

    # Hacer ping inicial inmediatamente
    ping_service(service_url)

    # Loop infinito con pings periódicos
    try:
        while True:
            time.sleep(ping_interval)
            ping_service(service_url)
    except KeyboardInterrupt:
        print("\n")
        print("=" * 70)
        print("⏹️  Servicio de Keep Alive detenido por el usuario")
        print("=" * 70)
        sys.exit(0)

if __name__ == "__main__":
    main()

