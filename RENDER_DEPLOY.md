# ============================================
# CONFIGURACIÓN PARA RENDER.COM
# ============================================

# 📋 INSTRUCCIONES DE DESPLIEGUE EN RENDER

## 1. Crear Base de Datos PostgreSQL

1. Ve a: https://dashboard.render.com
2. Click en "New +" → "PostgreSQL"
3. Configuración:
   - Name: `logicbot-db`
   - Database: `logicbot` (o el nombre que prefieras)
   - User: (se genera automáticamente)
   - Region: Oregon (US West) - Plan gratuito disponible
   - Plan: **Free** (0$/mes)
4. Click en "Create Database"
5. **MUY IMPORTANTE:** Copia el "Internal Database URL" (empieza con `postgresql://`)
   - Ejemplo: `postgresql://logicbot_user:abc123@dpg-xxxxx-a.oregon-postgres.render.com/logicbot_db`

## 2. Crear Web Service

1. En el dashboard de Render, click en "New +" → "Web Service"
2. Conecta tu repositorio de GitHub
3. Configuración del servicio:
   
   **General:**
   - Name: `logicbot-api` (o el nombre que prefieras)
   - Region: Oregon (US West) - Mismo que la BD
   - Branch: `main` (o `master`)
   - Root Directory: (dejar vacío)
   
   **Build & Deploy:**
   - Runtime: `Python 3`
   - Build Command: `./build.sh` o `pip install -r requirements.txt`
   - Start Command: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`
   
   **Plan:**
   - Instance Type: **Free** (0$/mes)
   
4. Click en "Advanced" para agregar variables de entorno

## 3. Configurar Variables de Entorno

En la sección "Environment Variables", agrega TODAS estas variables:

```
DATABASE_URL
└─ Valor: El "Internal Database URL" que copiaste en el paso 1

WHATSAPP_TOKEN
└─ Valor: Tu token de WhatsApp Business API
└─ Obtener en: https://developers.facebook.com/apps/

ID_NUMERO_TELEFONO
└─ Valor: Tu Phone Number ID de WhatsApp
└─ Obtener en: Meta Developers → WhatsApp → API Setup

GEMINI_API_KEY
└─ Valor: Tu API Key de Google Gemini
└─ Obtener en: https://aistudio.google.com/app/apikey

VERIFY_TOKEN
└─ Valor: Tu token secreto (mínimo 8 caracteres)
└─ Ejemplo: miBot2025_secreto

PYTHON_VERSION
└─ Valor: 3.11.0
└─ (Opcional, especifica la versión de Python)
```

**Cómo agregar cada variable:**
- Click en "Add Environment Variable"
- Key: Nombre de la variable (ej: `DATABASE_URL`)
- Value: El valor correspondiente
- Click en "Add"
- Repite para cada variable

## 4. Desplegar

1. Click en "Create Web Service"
2. Render automáticamente:
   - Clonará tu repositorio
   - Instalará las dependencias (`requirements.txt`)
   - Ejecutará el comando de inicio
   - Asignará una URL pública

3. Espera 3-5 minutos (primera vez puede tardar más)

4. Cuando veas "Live" en verde, copia la URL
   - Ejemplo: `https://logicbot-api.onrender.com`

## 5. Configurar Webhook de WhatsApp

1. Ve a: https://developers.facebook.com/apps/
2. Selecciona tu app → WhatsApp → Configuración
3. En "Webhook":
   - Click en "Configurar"
   - **Callback URL:** `https://tu-app.onrender.com/webhook`
   - **Verify token:** El valor de `VERIFY_TOKEN` que configuraste
4. Click en "Verificar y guardar"
5. Suscríbete al campo "messages"

## 6. Probar el Bot

1. Envía un mensaje a tu número de WhatsApp Business
2. Deberías recibir el mensaje de bienvenida
3. Si no funciona, revisa los logs en Render:
   - Dashboard → Tu servicio → Logs

---

## ⚠️ LIMITACIONES DEL PLAN GRATUITO DE RENDER

### Base de Datos PostgreSQL Free:
- **Almacenamiento:** 1 GB
- **Conexiones:** Limitadas
- **Duración:** 90 días (luego se elimina si no se usa)
- **Sin backups automáticos**

**Recomendación:** Exporta tu BD cada mes:
```bash
# Desde tu terminal local
pg_dump DATABASE_URL > backup_$(date +%Y%m%d).sql
```

### Web Service Free:
- **RAM:** 512 MB
- **CPU:** Compartida
- **Suspensión:** Se duerme después de 15 minutos de inactividad
  - Primera request después de despertar: 30-60 segundos
- **Límite mensual:** 750 horas (suficiente para 24/7)

**Problema del "cold start":**
- Solución 1: Usar un servicio de "ping" (ej: UptimeRobot) cada 14 minutos
- Solución 2: Actualizar a plan de pago ($7/mes para estar siempre activo)

---

## 🔄 FLUJO DE DESARROLLO RECOMENDADO

```
┌─────────────────────────────────────────────────────────┐
│  1. DESARROLLO LOCAL                                    │
│     - Trabaja en tu código                              │
│     - Prueba con uvicorn main:app --reload              │
│     - Usa .env para variables locales (NO SUBIR A GIT)  │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  2. COMMIT Y PUSH A GITHUB                              │
│     git add .                                           │
│     git commit -m "Descripción del cambio"              │
│     git push origin main                                │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  3. AUTO-DEPLOY EN RENDER                               │
│     - Render detecta el push automáticamente            │
│     - Ejecuta build.sh                                  │
│     - Reinicia el servicio                              │
│     - Tiempo estimado: 2-3 minutos                      │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  4. PRUEBAS EN PRODUCCIÓN                               │
│     - Envía mensajes al bot vía WhatsApp                │
│     - Revisa logs en Render Dashboard                   │
│     - Verifica que todo funciona correctamente          │
└─────────────────────────────────────────────────────────┘
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS EN RENDER

### Error: "Application failed to start"

**Revisar logs:**
1. Dashboard → Tu servicio → Logs
2. Busca el error específico

**Causas comunes:**
- ❌ `DATABASE_URL` mal configurada
- ❌ Falta alguna variable de entorno
- ❌ Error en `requirements.txt`
- ❌ Puerto incorrecto (Render usa la variable `PORT`)

**Solución:**
- Verifica todas las variables de entorno
- Asegúrate de que `requirements.txt` esté completo
- Render asigna el puerto automáticamente (no lo configures en código)

### Error: "Database connection refused"

**Causas:**
- Base de datos en otra región diferente al web service
- URL incorrecta (usa "Internal Database URL", NO "External")

**Solución:**
1. Ve a tu base de datos en Render
2. Copia "Internal Database URL"
3. Actualiza `DATABASE_URL` en las variables de entorno del web service

### El bot no responde después de 15 minutos

**Causa:** Render pone a dormir el servicio gratuito por inactividad

**Soluciones:**

**A) Mantener despierto con UptimeRobot (Gratis):**
1. Ve a: https://uptimerobot.com
2. Crea cuenta gratuita
3. Add New Monitor:
   - Monitor Type: HTTP(s)
   - Friendly Name: LogicBot Keep Alive
   - URL: `https://tu-app.onrender.com/webhook`
   - Monitoring Interval: 5 minutes (plan gratuito)
4. Guarda

**B) Actualizar a plan de pago:**
- Starter Plan: $7/mes
- Beneficios: Siempre activo, más RAM, más CPU

### Los logs no muestran nada

**Solución:**
Asegúrate de que tu código use `print()` para debugging:

```python
# En main.py, agrega más logs
print(f"📩 Mensaje recibido de: {numero_remitente}")
print(f"📝 Contenido: {mensaje_texto}")
```

---

## 📊 MONITOREO

### Ver logs en tiempo real:
```
Dashboard → Tu servicio → Logs → (se actualizan automáticamente)
```

### Métricas disponibles:
- CPU usage
- Memory usage
- Request count
- Response time

### Alertas (opcional):
- Configura notificaciones por email
- Settings → Notifications

---

## 🔐 SEGURIDAD

### Variables de entorno:
✅ **NUNCA** subas el archivo `.env` a GitHub  
✅ Usa `.gitignore` (ya incluido)  
✅ Configura variables sensibles SOLO en Render Dashboard  

### Tokens de WhatsApp:
⚠️ Los tokens temporales expiran en 24 horas  
✅ Genera un token permanente:
1. https://business.facebook.com/settings/system-users
2. Crea usuario de sistema
3. Asigna permisos de WhatsApp
4. Genera token que no expira

---

## 💰 COSTOS (Actualizado 2025)

### Plan Actual (Gratis):
- PostgreSQL Free: $0/mes
- Web Service Free: $0/mes
- **TOTAL: $0/mes**

### Si necesitas actualizar:
- PostgreSQL Starter: $7/mes (10 GB, sin suspensión)
- Web Service Starter: $7/mes (siempre activo, 512 MB RAM)
- **TOTAL: $14/mes**

---

## 📞 RECURSOS ÚTILES

- **Render Docs:** https://render.com/docs
- **Render Status:** https://status.render.com
- **Community Forum:** https://community.render.com
- **PostgreSQL Docs:** https://render.com/docs/databases

---

## ✅ CHECKLIST DE DEPLOYMENT

Antes de desplegar, verifica:

- [ ] Código funciona en local (`uvicorn main:app --reload`)
- [ ] `requirements.txt` está actualizado
- [ ] `.gitignore` incluye `.env`
- [ ] `.env` NO está en el repositorio
- [ ] Código subido a GitHub
- [ ] Base de datos PostgreSQL creada en Render
- [ ] Web Service creado y conectado al repo
- [ ] Todas las variables de entorno configuradas
- [ ] Build Command correcto
- [ ] Start Command correcto
- [ ] Servicio desplegado exitosamente (estado "Live")
- [ ] Webhook de WhatsApp configurado
- [ ] Bot probado y funcionando

---

**Última actualización:** 2025-11-17  
**Render Free Tier Status:** Activo

