"""
    main()
if __name__ == "__main__":

        sys.exit(0)
        print("=" * 70)
        print("⏹️  Servicio de Keep Alive detenido por el usuario")
        print("=" * 70)
        print("\n")
    except KeyboardInterrupt:

            ping_service(service_url)
            time.sleep(ping_interval)
        while True:
    try:
    # Loop infinito con pings periódicos

    ping_service(service_url)
    # Hacer ping inicial inmediatamente

    print()
    print("=" * 70)
    print(f"🚀 Iniciando monitoreo...")
    print(f"⏰ Intervalo de ping: {ping_interval // 60} minutos")
    print(f"🎯 Servicio objetivo: {service_url}")
    print("=" * 70)
    print("🤖 LogicBot - Keep Alive Service")
    print("=" * 70)

    ping_interval = 14 * 60  # 14 minutos en segundos (Render suspende después de 15 min)
    service_url = sys.argv[1]

        sys.exit(1)
        print("Uso: python keep_alive.py https://chatbot-ai-logica-de-programacion.onrender.com")
        print("❌ Error: Debes proporcionar la URL del servicio")
    if len(sys.argv) < 2:
def main():

        return False
        print(f"[{timestamp}] ❌ Error al hacer ping: {e}")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    except requests.exceptions.RequestException as e:

        return False
        print(f"[{timestamp}] ⏱️  Timeout - El servicio puede estar despertando (cold start)")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    except requests.exceptions.Timeout:

            return False
            print(f"[{timestamp}] ⚠️  Ping respondió con código: {response.status_code}")
        else:
            return True
            print(f"[{timestamp}] ✅ Ping exitoso - Status: {data.get('status')} - Uptime: {data.get('uptime')}")
            data = response.json()
        if response.status_code == 200:

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        response = requests.get(health_url, timeout=30)
        health_url = f"{url.rstrip('/')}/health"
        # Ping al endpoint de health check
    try:
    """
    Hace un ping al servicio para mantenerlo despierto.
    """
def ping_service(url):

from datetime import datetime
import sys
import time
import requests

"""
    python keep_alive.py https://chatbot-ai-logica-de-programacion.onrender.com
USO:

Ejecuta pings cada 14 minutos para evitar que el servicio gratuito se suspenda.
Script para mantener el servicio de Render despierto.

