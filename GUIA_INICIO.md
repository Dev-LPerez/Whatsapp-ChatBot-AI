# 🚀 GUÍA DE INICIO RÁPIDO - LogicBot

## 📋 ANTES DE EMPEZAR

Has completado el análisis del proyecto. Ahora sigue estos pasos para ponerlo en marcha:

---

## ✅ PASO 1: Activar el Entorno Virtual

### Windows (PowerShell):
```powershell
cd "C:\Users\LUIS PEREZ\OneDrive\Desktop\Whatsapp-ChatBot-AI"
.venv\Scripts\Activate.ps1
```

### Si da error de permisos:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
```

### Verificar activación:
Deberías ver `(.venv)` al inicio de tu línea de comandos.

---

## ✅ PASO 2: Instalar Dependencias

```powershell
pip install -r requirements.txt
```

**Tiempo estimado:** 2-3 minutos

**Qué instala:**
- FastAPI (servidor web)
- SQLAlchemy (base de datos)
- Google Genai (IA)
- Requests (WhatsApp API)
- Y 64 paquetes más...

---

## ✅ PASO 3: Configurar Variables de Entorno

### 3.1 Crear archivo .env

```powershell
Copy-Item .env.example .env
```

### 3.2 Editar .env con tus credenciales

Abre `.env` con tu editor favorito y completa:

```bash
# --- BASE DE DATOS ---
DATABASE_URL=postgresql://usuario:password@host:5432/nombre_bd

# --- WHATSAPP ---
WHATSAPP_TOKEN=EAAxxxxxxxxxxxxxxxxxx
ID_NUMERO_TELEFONO=123456789012345

# --- GOOGLE GEMINI ---
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxx

# --- WEBHOOK ---
VERIFY_TOKEN=micodigosecreto_12345
```

### 3.3 ¿Dónde obtener cada valor?

#### 📊 DATABASE_URL

**Opción A: PostgreSQL Local (Desarrollo)**
```bash
# Instala PostgreSQL desde: https://www.postgresql.org/download/
# Crea una base de datos llamada 'logicbot'
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/logicbot
```

**Opción B: PostgreSQL en la Nube (Producción - RECOMENDADO)**

**Railway.app (Gratis):**
1. Ve a: https://railway.app
2. Crea cuenta con GitHub
3. New Project > Database > PostgreSQL
4. Copia el "PostgreSQL Connection URL"
5. Pégalo en `.env` como `DATABASE_URL=...`

**Render.com (Gratis):**
1. Ve a: https://render.com
2. New > PostgreSQL
3. Copia "External Database URL"

#### 📱 WHATSAPP_TOKEN e ID_NUMERO_TELEFONO

1. Ve a: https://developers.facebook.com/apps/
2. Crea una app (tipo: Business)
3. Agrega producto "WhatsApp"
4. En "API Setup":
   - **Token de acceso temporal** → Copia como `WHATSAPP_TOKEN`
   - **Phone Number ID** → Copia como `ID_NUMERO_TELEFONO`

**IMPORTANTE:** El token temporal expira en 24h. Para uno permanente:
- Ve a: https://business.facebook.com/settings/system-users
- Crea usuario de sistema
- Genera token permanente con permisos de WhatsApp

#### 🤖 GEMINI_API_KEY

1. Ve a: https://aistudio.google.com/app/apikey
2. Inicia sesión con tu cuenta Google
3. Click en "Create API Key"
4. Copia la key generada

**Límites gratuitos:**
- 60 requests/minuto
- 1,500 requests/día

#### 🔐 VERIFY_TOKEN

Este lo creas tú. Debe ser:
- Alfanumérico
- Mínimo 8 caracteres
- Ejemplo: `miBot2025_secreto`

**Importante:** Lo usarás más adelante al configurar el webhook.

---

## ✅ PASO 4: Verificar Configuración

```powershell
python verificar_config.py
```

**Deberías ver:**
```
✅ Python 3.11+
✅ Archivos del proyecto
✅ Variables de entorno
✅ Librerías instaladas
```

---

## ✅ PASO 5: Iniciar el Servidor

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Verás:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**¡El servidor ya está corriendo! 🎉**

---

## ✅ PASO 6: Exponer el Webhook Localmente (Solo para Pruebas)

### Opción A: Usar Ngrok (Recomendado)

```powershell
# Instala ngrok desde: https://ngrok.com/download
ngrok http 8000
```

**Obtendrás una URL pública como:**
```
https://abc123xyz.ngrok-free.app
```

**Copia esta URL** (la necesitarás en el siguiente paso).

### Opción B: Usar Localhost.run (Sin instalación)

```powershell
ssh -R 80:localhost:8000 nokey@localhost.run
```

---

## ✅ PASO 7: Configurar Webhook en Meta Developers

1. Ve a: https://developers.facebook.com/apps/
2. Selecciona tu app > WhatsApp > Configuración
3. Click en "Configurar" (en la sección Webhook)

**Completa:**
- **URL del webhook:** `https://tu-url-ngrok.com/webhook`
- **Token de verificación:** El valor de `VERIFY_TOKEN` de tu `.env`

4. Click en "Verificar y guardar"

**Si todo está bien, verás un ✓ verde.**

5. En "Campos del webhook", activa:
   - ✅ messages

---

## ✅ PASO 8: ¡Probar el Bot!

1. Abre WhatsApp
2. Envía cualquier mensaje al número de tu WhatsApp Business
3. Deberías recibir:
   ```
   ¡Hola, [Tu Nombre]! 👋 
   Soy LogicBot, tu tutor de IA personal. 
   ¡Estoy aquí para ayudarte a pensar como un programador! 🚀
   
   [Ver Menú Principal]
   ```

4. Click en el botón
5. ¡Explora las opciones!

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### ❌ Error: "Referencia no resuelta 'fastapi'"

**Causa:** Dependencias no instaladas  
**Solución:**
```powershell
pip install -r requirements.txt
```

### ❌ Error: "DATABASE_URL not found"

**Causa:** Archivo `.env` no existe o no se cargó  
**Solución:**
1. Verifica que `.env` existe en la raíz del proyecto
2. Reinicia el servidor: `uvicorn main:app --reload`

### ❌ Error: "Connection refused" al conectar a PostgreSQL

**Causa:** PostgreSQL no está corriendo  
**Solución:**
- **Local:** Inicia el servicio de PostgreSQL
- **Cloud:** Verifica que la URL de Railway/Render es correcta

### ❌ El webhook no se verifica

**Posibles causas:**
1. **URL incorrecta:** Asegúrate de que termina en `/webhook`
2. **Token incorrecto:** Debe coincidir con `VERIFY_TOKEN` del `.env`
3. **Servidor no accesible:** Verifica que ngrok está corriendo

**Verificación manual:**
```powershell
# Reemplaza TU_URL y TU_TOKEN
curl "https://tu-url.ngrok.io/webhook?hub.mode=subscribe&hub.verify_token=TU_TOKEN&hub.challenge=1234"
```

Debería devolver: `1234`

### ❌ El bot no responde a mensajes

**Checklist:**
1. ✅ Servidor corriendo (`uvicorn`)
2. ✅ Ngrok activo (URL pública)
3. ✅ Webhook verificado en Meta
4. ✅ Campo "messages" suscrito
5. ✅ `WHATSAPP_TOKEN` válido (no expirado)

**Debug:**
Mira la consola donde corre `uvicorn`. Deberías ver:
```json
{
  "entry": [...],
  "messages": [...]
}
```

Si no ves nada, el webhook no está enviando datos.

---

## 🚀 DESPLIEGUE EN PRODUCCIÓN

### Railway.app (RECOMENDADO - Muy fácil)

1. **Sube tu código a GitHub** (si no lo has hecho)
   ```powershell
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/tu-usuario/logicbot.git
   git push -u origin main
   ```

2. **Ve a Railway.app**
   - https://railway.app
   - Login con GitHub
   - New Project > Deploy from GitHub repo
   - Selecciona tu repositorio

3. **Agrega PostgreSQL**
   - En tu proyecto > New > Database > PostgreSQL
   - Se crea automáticamente

4. **Configura Variables**
   - Click en tu servicio web
   - Variables > New Variable
   - Agrega una por una:
     - `DATABASE_URL` (se autocompletará desde PostgreSQL)
     - `WHATSAPP_TOKEN`
     - `ID_NUMERO_TELEFONO`
     - `GEMINI_API_KEY`
     - `VERIFY_TOKEN`

5. **Deploy**
   - Railway detecta automáticamente el `Procfile`
   - Click en "Deploy"
   - Obtendrás una URL pública como: `https://logicbot-production.up.railway.app`

6. **Actualiza el webhook**
   - Ve a Meta Developers
   - Cambia la URL del webhook a tu URL de Railway
   - Ejemplo: `https://logicbot-production.up.railway.app/webhook`

**¡Listo! Tu bot está en producción 24/7 🎉**

---

## 📊 MONITOREO

### Ver logs en tiempo real:

**Local:**
```powershell
# Ya los ves en la terminal donde corre uvicorn
```

**Railway:**
- Dashboard > Tu servicio > Deployments > View Logs

**Render:**
- Dashboard > Tu servicio > Logs

---

## 🎓 PRÓXIMOS PASOS

Ahora que tu bot está funcionando:

1. **Prueba todas las funciones:**
   - Menú de temas de Java
   - Retos aleatorios
   - Sistema de puntos
   - Comandos (`menu`, `me rindo`, `mi perfil`)

2. **Personaliza:**
   - Edita `config.py` para agregar más temas
   - Ajusta `PUNTOS_POR_DIFICULTAD`
   - Modifica mensajes de bienvenida en `main.py`

3. **Expande:**
   - Agrega soporte para Python (edita `config.py`)
   - Implementa sistema de logros
   - Crea un dashboard web

4. **Comparte:**
   - Invita amigos a probar el bot
   - Documenta tu experiencia
   - Contribuye mejoras al proyecto

---

## 📞 RECURSOS ÚTILES

- **Documentación FastAPI:** https://fastapi.tiangolo.com
- **WhatsApp Cloud API:** https://developers.facebook.com/docs/whatsapp/cloud-api
- **Google Gemini API:** https://ai.google.dev/docs
- **Railway Docs:** https://docs.railway.app
- **PostgreSQL Tutorial:** https://www.postgresqltutorial.com

---

## ✅ CHECKLIST FINAL

Antes de considerar el proyecto completo:

- [ ] Dependencias instaladas
- [ ] Archivo `.env` configurado
- [ ] PostgreSQL funcionando (local o cloud)
- [ ] Servidor local corriendo sin errores
- [ ] Webhook configurado y verificado
- [ ] Bot responde a mensajes
- [ ] Todas las funciones probadas:
  - [ ] Registro de nuevo usuario
  - [ ] Menú de temas de Java
  - [ ] Generación de retos
  - [ ] Evaluación de código
  - [ ] Sistema de puntos
  - [ ] Perfil de usuario
  - [ ] Comando "me rindo"
- [ ] Desplegado en producción (Railway/Heroku/Render)
- [ ] Documentación actualizada

---

## 🎉 ¡FELICIDADES!

Has completado la configuración de **LogicBot**, un chatbot educativo de nivel profesional.

**¿Preguntas? ¿Problemas?**
- Revisa la sección "Solución de Problemas"
- Consulta el `README.md`
- Verifica los logs del servidor

**¡Disfruta enseñando Java con IA! 🚀📱🤖**

---

**Última actualización:** 2025-01-17  
**Versión:** 1.0 - Gemini 2.0 Flash Edition

