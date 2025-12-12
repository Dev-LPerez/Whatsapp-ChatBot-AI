# 🔧 Troubleshooting - Render Deploy

Guía de solución de problemas comunes al desplegar en Render.

---

## ❌ Error: "ModuleNotFoundError: No module named 'main'"

### Síntoma
```
ModuleNotFoundError: No module named 'main'
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/bin/gunicorn", line 8, in <module>
    ...
  File "/opt/render/project/src/.venv/lib/python3.11/site-packages/gunicorn/util.py", line 370, in import_app
    mod = importlib.import_module(module)
```

### Causa
El `Procfile` está configurado con el comando antiguo `main:app` en lugar de `src.main:app`.

### Solución

#### Opción 1: Limpiar Cache de Render (Recomendado)

1. Ve al **Dashboard de Render**
2. Selecciona tu servicio
3. Ve a **Settings** → **Build & Deploy**
4. Haz clic en **"Clear build cache & deploy"**
5. Espera a que se complete el nuevo deploy

#### Opción 2: Forzar Rebuild desde Git

```bash
# Hacer un commit vacío para forzar rebuild
git commit --allow-empty -m "chore: force render rebuild"
git push origin main
```

#### Opción 3: Verificar Procfile Manualmente

1. Verifica que tu `Procfile` tenga exactamente:
   ```
   web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app
   ```

2. Si está correcto pero Render usa la versión vieja:
   ```bash
   # Edita el Procfile, guarda y haz commit
   git add Procfile
   git commit -m "fix: update Procfile with correct module path"
   git push origin main
   ```

---

## ❌ Error: Firebase Admin SDK no Inicializa

### Síntoma
```
❌ Error inicializando Firebase: ...
❌ No se pudo conectar a Firestore. Verifica las credenciales.
```

### Soluciones

#### Para Desarrollo Local

1. Descarga las credenciales de Firebase:
   - Ve a [Firebase Console](https://console.firebase.google.com/)
   - Proyecto → Configuración → Cuentas de Servicio
   - Genera nueva clave privada
   
2. Guarda el archivo como:
   ```
   src/config/firebase_credentials.json
   ```

3. Verifica que esté en `.gitignore`:
   ```gitignore
   firebase_credentials.json
   src/config/firebase_credentials.json
   ```

#### Para Producción (Render)

El bot usa credenciales por defecto automáticamente. Asegúrate de:

1. Tener configurado Google Cloud Application Default Credentials
2. O usar variables de entorno de Firebase en Render

---

## ❌ Error: Variables de Entorno No Cargadas

### Síntoma
```
✗ WHATSAPP_TOKEN = NO CONFIGURADA
✗ GEMINI_API_KEY = NO CONFIGURADA
```

### Solución en Render

1. Ve a tu servicio en Render Dashboard
2. **Settings** → **Environment**
3. Agrega las siguientes variables:

```
WHATSAPP_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
VERIFY_TOKEN=micodigosecreto_12345
ID_NUMERO_TELEFONO=123456789012345
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

4. **Save Changes**
5. Render reiniciará automáticamente el servicio

### Solución en Local

1. Copia `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edita `.env` con tus valores reales

3. Reinicia el servidor

---

## ❌ Error: El Bot No Responde en WhatsApp

### Verificaciones

#### 1. Webhook Configurado Correctamente

- URL del webhook: `https://tu-app.onrender.com/webhook`
- Método: `POST`
- Verify Token: Mismo que en tu `.env`

#### 2. Verificar Logs en Render

```bash
# En el Dashboard de Render → Logs
# Busca errores como:
- 404 Not Found
- 500 Internal Server Error
- Connection timeout
```

#### 3. Probar Endpoint Manualmente

```bash
# Health check
curl https://tu-app.onrender.com/

# Debería responder:
{
  "status": "LogicBot activo",
  "version": "1.0.3",
  "uptime": "..."
}
```

#### 4. Verificar Subscripción a Eventos

En Meta Developers → WhatsApp → Configuration:

- ✅ `messages`
- ✅ `messaging_postbacks` (si usas botones)

---

## ❌ Error: Build Timeout en Render

### Síntoma
```
==> Build failed: Command timed out after 15 minutes
```

### Soluciones

1. **Optimizar `requirements.txt`** - Remover dependencias innecesarias

2. **Usar versiones específicas** - Evitar resolver dependencias en cada build:
   ```txt
   # requirements.txt
   fastapi==0.116.1
   uvicorn==0.35.0
   # etc...
   ```

3. **Upgrade Plan** - Los planes gratuitos tienen límites de tiempo

---

## ❌ Error: Application Failed to Start

### Síntoma
```
==> Exited with status 1
```

### Checklist

- [ ] `Procfile` tiene la ruta correcta: `src.main:app`
- [ ] Variables de entorno configuradas en Render
- [ ] `requirements.txt` instalado correctamente
- [ ] No hay errores de sintaxis en el código
- [ ] Puerto configurado correctamente (Render asigna automáticamente)

### Debug

Ejecuta localmente para ver el error exacto:

```bash
# Activar entorno virtual
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # Linux/Mac

# Ejecutar como lo hace Render
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app
```

---

## 📊 Comandos Útiles de Diagnóstico

### Verificar Configuración Local

```bash
python -m src.scripts.verificar_config
```

### Verificar Estructura del Proyecto

```bash
# Windows
tree /F src

# Linux/Mac
tree src
```

### Ver Logs en Tiempo Real (Render)

1. Dashboard → Tu Servicio → Logs
2. Habilita "Auto-scroll"
3. Filtra por tipo: `Errors` o `All`

---

## 🆘 Recursos Adicionales

- [Render Docs - Troubleshooting](https://render.com/docs/troubleshooting-deploys)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)

---

## 💬 ¿Aún Tienes Problemas?

1. Revisa los logs completos en Render
2. Ejecuta el bot localmente para identificar el error
3. Verifica que todas las dependencias estén instaladas
4. Contacta al equipo en GitHub Issues

---

**Última actualización**: 2025-01-12

