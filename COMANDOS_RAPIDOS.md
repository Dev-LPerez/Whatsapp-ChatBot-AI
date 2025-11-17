# ⚡ COMANDOS RÁPIDOS - LogicBot en Render

## 🚀 FLUJO DE TRABAJO DIARIO

### Paso 1: Hacer cambios en el código
```bash
# Edita tus archivos en tu editor favorito
# Guarda los cambios
```

### Paso 2: Subir a Git y desplegar
```bash
# Navega a la carpeta del proyecto
cd "C:\Users\LUIS PEREZ\OneDrive\Desktop\Whatsapp-ChatBot-AI"

# Ver archivos modificados
git status

# Agregar todos los cambios
git add .

# Hacer commit (cambia el mensaje)
git commit -m "Descripción de los cambios realizados"

# Subir a GitHub (esto dispara auto-deploy en Render)
git push origin main
```

### Paso 3: Verificar despliegue en Render
```bash
# Espera 2-3 minutos y luego verifica
curl https://tu-app.onrender.com/health
```

### Paso 4: Probar el bot
```
# Envía un mensaje a tu número de WhatsApp Business
# Verifica que funcione correctamente
```

---

## 🔍 DIAGNÓSTICO Y DEBUGGING

### Ver estado del proyecto local
```bash
python diagnostico_render.py
```

### Ver estado del servicio en producción
```bash
curl https://tu-app.onrender.com/health
```

### Mantener servicio despierto (ejecutar en terminal separada)
```bash
python keep_alive.py https://tu-app.onrender.com
```

### Ver logs en tiempo real
```
# Ve a: https://dashboard.render.com
# Selecciona tu servicio → Logs
```

---

## 📝 COMANDOS GIT ÚTILES

### Ver historial de commits
```bash
git log --oneline -5
```

### Deshacer último commit (manteniendo cambios)
```bash
git reset --soft HEAD~1
```

### Ver diferencias antes de commit
```bash
git diff
```

### Ver archivos que serán commiteados
```bash
git status
```

### Actualizar desde GitHub (si editaste en otro lugar)
```bash
git pull origin main
```

---

## 🐛 SOLUCIÓN RÁPIDA DE PROBLEMAS

### El bot no responde
```bash
# 1. Verificar que el servicio esté activo
curl https://tu-app.onrender.com/health

# 2. Ver logs en Render Dashboard
# 3. Verificar que el webhook esté configurado correctamente
```

### Error de base de datos
```bash
# Verificar que DATABASE_URL esté configurada en Render
# Dashboard → Tu servicio → Environment → DATABASE_URL
```

### Servicio suspendido (cold start)
```bash
# Configurar UptimeRobot o ejecutar:
python keep_alive.py https://tu-app.onrender.com
```

### Error después de push
```bash
# 1. Ver logs en Render
# 2. Verificar que requirements.txt esté actualizado
# 3. Verificar que no haya errores de sintaxis
```

---

## 🔄 ACTUALIZAR DEPENDENCIAS

### Agregar nueva librería
```bash
# 1. Instalar localmente (opcional para probar)
pip install nombre-libreria

# 2. Actualizar requirements.txt
pip freeze > requirements.txt

# 3. Hacer commit y push
git add requirements.txt
git commit -m "Agregar nueva dependencia: nombre-libreria"
git push origin main
```

---

## 📊 MONITOREO

### Verificar uptime
```bash
curl https://tu-app.onrender.com/health | python -m json.tool
```

### Ver métricas
```
# Dashboard de Render → Tu servicio → Metrics
# Verás: CPU, RAM, Request count
```

---

## 🔧 VARIABLES DE ENTORNO

### Ver variables configuradas
```
# Dashboard de Render → Tu servicio → Environment
```

### Agregar/editar variable
```
# Dashboard → Environment → Add Environment Variable
# Key: NOMBRE_VARIABLE
# Value: valor
# Save Changes → Render redesplegará automáticamente
```

---

## 💾 BACKUP DE BASE DE DATOS

### Exportar BD (desde Render Dashboard)
```
# 1. Ve a tu base de datos PostgreSQL en Render
# 2. Connect → External Connection → Copia el comando
# 3. Ejecuta localmente:

pg_dump "postgresql://user:pass@host/db" > backup_$(date +%Y%m%d).sql
```

### Importar backup (si necesitas restaurar)
```bash
psql "postgresql://user:pass@host/db" < backup_20251117.sql
```

---

## 🎯 ATAJOS ÚTILES

### Deploy rápido (un solo comando)
```bash
git add . && git commit -m "Update" && git push origin main
```

### Ver estado completo
```bash
git status && python diagnostico_render.py
```

### Verificar todo antes de push
```bash
python diagnostico_render.py && git status
```

---

## 📞 ENLACES RÁPIDOS

- **Render Dashboard:** https://dashboard.render.com
- **Meta Developers:** https://developers.facebook.com/apps/
- **Google AI Studio:** https://aistudio.google.com/app/apikey
- **UptimeRobot:** https://uptimerobot.com
- **GitHub Repo:** https://github.com/tu-usuario/tu-repo

---

## ✅ CHECKLIST DIARIA

Al final de cada sesión de desarrollo:

- [ ] Código funciona sin errores
- [ ] Cambios guardados
- [ ] Commit realizado con mensaje descriptivo
- [ ] Push a GitHub exitoso
- [ ] Render desplegó correctamente (check en dashboard)
- [ ] Bot probado en WhatsApp
- [ ] Logs revisados (sin errores críticos)

---

**Guarda este archivo en favoritos para acceso rápido a comandos comunes**

