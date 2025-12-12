# 🤖 LogicBot - Chatbot Educativo de Programación

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.3-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**Un asistente inteligente de programación que vive en WhatsApp 📱**

[Características](#-características) • [Demo](#-demo) • [Instalación](#-instalación) • [Uso](#-uso) • [API](#-api-reference)

</div>

---

## 📖 Descripción

**LogicBot** es un chatbot educativo basado en IA que enseña programación a través de WhatsApp Business API. Ofrece una experiencia de aprendizaje personalizada, interactiva y gamificada, adaptándose al nivel de cada estudiante.

### 🎯 Problema que Resuelve

- **Accesibilidad**: Aprende desde WhatsApp, sin necesidad de apps adicionales
- **Personalización**: Retos adaptados a tu nivel y preferencias
- **Motivación**: Sistema de gamificación con puntos, logros y rachas
- **Feedback Inmediato**: Evaluación instantánea con IA (Google Gemini)
- **Disponibilidad 24/7**: Practica cuando quieras, donde quieras

---

## ✨ Características

### 🎓 Sistema de Aprendizaje

- **Onboarding Inteligente**: Quiz inicial para determinar tu nivel
- **Curso de Java**: 7 lecciones progresivas (Variables, Operadores, Condicionales, Bucles, Arrays, Métodos, POO)
- **Retos Dinámicos**: Generados con IA según tu nivel y tema
- **3 Dificultades**: Fácil (10pts), Intermedio (20pts), Difícil (30pts)
- **Evaluación con IA**: Feedback detallado usando Google Gemini 2.0
- **Ayuda Contextual**: Pistas automáticas tras fallos repetidos

### 🎮 Gamificación

- **Sistema de Puntos**: Gana puntos por cada reto completado
- **Niveles Progresivos**: 6 niveles desde Aprendiz 🌱 hasta Leyenda ⭐
- **Logros Desbloqueables**: 5 medallas (Primer Paso, Aprendiz, Consistente, Dedicado, Maestro)
- **Rachas de Estudio**: Mantén tu motivación con rachas diarias 🔥
- **Fichas Técnicas**: Biblioteca de recursos desbloqueables

---

## 📂 Estructura del Proyecto

El proyecto ha sido reestructurado para una mejor organización y escalabilidad.

```
.
├── src/
│   ├── __init__.py
│   ├── main.py                   # Punto de entrada (FastAPI)
│   ├── ai_services.py            # Integración con Gemini AI
│   ├── database.py               # Lógica de Firebase
│   ├── message_handler.py        # Enrutamiento de mensajes
│   ├── whatsapp_utils.py         # Funciones de WhatsApp API
│   │
│   ├── config/
│   │   ├── config.py             # Configuración global
│   │   └── firebase_credentials.json.example
│   │
│   ├── message_components/       # Componentes modulares
│   │   ├── __init__.py
│   │   ├── achievements.py       # Sistema de logros
│   │   └── onboarding.py         # Flujo de bienvenida
│   │
│   ├── scripts/                  # Scripts de utilidad
│   │   ├── diagnostico_render.py # Diagnóstico para Render
│   │   ├── keep_alive.py         # Health check para Render
│   │   └── verificar_config.py   # Verificar configuración
│   │
│   └── utils/                    # Utilidades
│       ├── __init__.py
│       ├── emojis.py             # Constantes de emojis
│       └── formatters.py         # Formateadores de texto
│
├── tests/                        # Tests (en desarrollo)
├── __pycache__/
├── .venv/                        # Entorno virtual (local)
├── .git/
├── .gitignore
├── .env.example                  # Plantilla de variables de entorno
├── build.sh                      # Script de build para Render
├── Procfile                      # Config para Render
├── README.md                     # Este archivo
├── requirements.txt              # Dependencias Python
└── firebase_credentials.json     # Credenciales Firebase (no subir a Git)
```

---

## 🚀 Demo

### Flujo de Usuario

```
Usuario: ¡Hola! 👋
LogicBot: ¡Bienvenido a LogicBot! 🤖 
         ¿Cómo te llamas?

Usuario: Luis
LogicBot: [Inicia onboarding con botones]
         ¿Cuál es tu nivel de programación?
         [Principiante] [Intermedio] [Avanzado]

Usuario: [Selecciona Intermedio]
LogicBot: 📚 Menú Principal:
         🎯 Curso de Java
         ⚡ Reto Rápido
         🎒 Mi Mochila
         📊 Mi Perfil

Usuario: [Selecciona Reto Rápido]
LogicBot: 💡 RETO - Dificultad: Intermedio (20 pts)
         
         Escribe una función que...
         [enunciado generado por IA]
```

### Capturas de Pantalla

> **Nota**: El bot funciona directamente desde WhatsApp con interfaz de botones interactivos

---

## 🛠️ Tecnologías

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web moderno y rápido
- **[Python 3.11+](https://www.python.org/)** - Lenguaje principal
- **[Uvicorn](https://www.uvicorn.org/)** - Servidor ASGI

### Base de Datos
- **[Firebase Firestore](https://firebase.google.com/docs/firestore)** - Base de datos NoSQL en tiempo real
- **[Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)** - Autenticación y gestión

### Inteligencia Artificial
- **[Google Gemini AI](https://ai.google.dev/)** - Generación y evaluación de retos
- **Modelo**: `gemini-2.0-flash` - Optimizado para respuestas rápidas

### APIs Externas
- **[WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)** - Mensajería
- **Meta Graph API** - Envío de mensajes interactivos

### Despliegue
- **[Render](https://render.com/)** - Hosting y CD/CI
- **GitHub** - Control de versiones

---

## 📦 Instalación

### Prerrequisitos

- Python 3.11 o superior
- Cuenta de WhatsApp Business API
- Cuenta de Google Cloud (para Gemini AI)
- Proyecto de Firebase configurado

### 1️⃣ Clonar el Repositorio

```powershell
git clone https://github.com/tu-usuario/Whatsapp-ChatBot-AI.git
cd Whatsapp-ChatBot-AI
```

### 2️⃣ Crear Entorno Virtual

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Si hay error de permisos:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3️⃣ Instalar Dependencias

```powershell
pip install -r requirements.txt
```

### 4️⃣ Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto (puedes copiar `.env.example`):

```env
# WhatsApp Business API
WHATSAPP_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
VERIFY_TOKEN=micodigosecreto_12345
ID_NUMERO_TELEFONO=123456789012345

# Google Gemini AI
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Base de Datos (si no usas Firebase)
# DATABASE_URL=postgresql://usuario:password@host:5432/nombre_bd
```

### 5️⃣ Configurar Firebase

**Opción 1: Usando archivo de credenciales (Recomendado para desarrollo local)**

Descarga tu archivo de credenciales desde la consola de Firebase:

**Pasos:**
1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto
3. Ve a **Configuración del Proyecto** > **Cuentas de Servicio**
4. Clic en **Generar nueva clave privada**
5. Guarda el archivo como `firebase_credentials.json` en `src/config/firebase_credentials.json`

**⚠️ IMPORTANTE: Este archivo contiene credenciales sensibles**
- **NUNCA** lo subas a Git (ya está en `.gitignore`)
- Usa `src/config/firebase_credentials.json.example` como referencia
- En producción, usa las credenciales por defecto de Render/Google Cloud

**Opción 2: Usando credenciales por defecto (Recomendado para producción)**

El bot automáticamente intentará usar las credenciales por defecto si no encuentra el archivo local, ideal para despliegue en Render con Google Cloud.

```python
# El código en database.py maneja ambos casos automáticamente
if os.path.exists("src/config/firebase_credentials.json"):
    cred = credentials.Certificate("src/config/firebase_credentials.json")
else:
    # Usa credenciales por defecto en producción
    firebase_admin.initialize_app()
```

### 6️⃣ Verificar Configuración

```powershell
python -m src.scripts.verificar_config
```

Deberías ver:
```
✅ WhatsApp configurado
✅ Gemini AI configurado
✅ Firebase configurado
```

---

## 🚀 Uso

### Modo Desarrollo (Local)

```powershell
uvicorn src.main:app --reload --port 8000
```

O alternativamente:

```powershell
python -m uvicorn src.main:app --reload --port 8000
```

El servidor estará disponible en `http://localhost:8000`

### Modo Producción (Render)

El proyecto incluye configuración automática para Render:

1. **Archivo `Procfile`**: Define el comando de inicio con Gunicorn
   ```
   web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app
   ```
   ⚠️ **Importante**: El comando debe ser `src.main:app` (no `main:app`)
   
2. **Script `build.sh`**: Instalación de dependencias
   ```bash
   pip install -r requirements.txt
   ```

3. **Variables de Entorno**: Configuradas en Render Dashboard
   - `WHATSAPP_TOKEN`
   - `VERIFY_TOKEN`
   - `ID_NUMERO_TELEFONO`
   - `GEMINI_API_KEY`

4. **Despliegue**:
   - Automático al hacer push a la rama `main`
   - Si hay errores de cache, usa: **Settings → Clear build cache & deploy**

**URL del servicio**: `https://tu-app.onrender.com`

### Configurar Webhook de WhatsApp

1. Ve a la [Meta App Dashboard](https://developers.facebook.com/)
2. Configura el webhook con tu URL de Render:
   ```
   https://tu-app.onrender.com/webhook
   ```
3. Token de verificación: El valor de `VERIFY_TOKEN` en tu `.env`
4. Suscríbete a eventos: `messages`

---

## 📱 Comandos del Bot

| Comando | Descripción |
|---------|-------------|
| **Hola** / **Inicio** | Activa el bot y muestra el menú principal |
| **Menú** | Regresa al menú principal |
| **Perfil** | Muestra tu progreso, nivel y puntos |
| **Logros** | Ver medallas desbloqueadas |
| **Fichas** | Biblioteca de recursos técnicos |
| **Ayuda** | Información sobre cómo usar el bot |

### Navegación por Botones

El bot usa **menús interactivos** de WhatsApp:
- 📚 **Aprender**: Curso de Java o Retos Rápidos
- 🎒 **Mi Mochila**: Perfil, Logros, Fichas
- ⚡ **Acciones Rápidas**: Botones de respuesta

---

## 🏗️ Arquitectura

### Estructura del Proyecto

```
Whatsapp-ChatBot-AI/
│
├── src/                       # Código fuente principal
│   ├── __init__.py
│   ├── main.py               # Punto de entrada (FastAPI)
│   ├── database.py           # Lógica de Firebase
│   ├── ai_services.py        # Integración con Gemini AI
│   ├── message_handler.py    # Enrutamiento de mensajes
│   ├── whatsapp_utils.py     # Funciones de WhatsApp API
│   │
│   ├── config/               # Configuraciones
│   │   ├── config.py         # Configuración global
│   │   └── firebase_credentials.json.example
│   │
│   ├── message_components/   # Componentes modulares
│   │   ├── __init__.py
│   │   ├── onboarding.py     # Flujo de bienvenida
│   │   └── achievements.py   # Sistema de logros
│   │
│   ├── scripts/              # Scripts de utilidad
│   │   ├── verificar_config.py    # Script de diagnóstico
│   │   ├── diagnostico_render.py  # Diagnóstico para Render
│   │   └── keep_alive.py          # Health check para Render
│   │
│   └── utils/                # Utilidades
│       ├── __init__.py
│       ├── emojis.py         # Constantes de emojis
│       └── formatters.py     # Formateadores de texto
│
├── tests/                    # Tests (en desarrollo)
├── .venv/                    # Entorno virtual (local)
├── __pycache__/              # Cache de Python
├── .gitignore
├── .env.example              # Plantilla de variables de entorno
├── build.sh                  # Script de build para Render
├── Procfile                  # Config para Render (Gunicorn)
├── requirements.txt          # Dependencias Python
├── firebase_credentials.json # Credenciales Firebase (no subir a Git)
└── README.md                 # Este archivo
```

### Flujo de Datos

```
WhatsApp User
     │
     ├─► POST /webhook (FastAPI)
     │        │
     │        ├─► message_handler.py
     │        │        │
     │        │        ├─► Identifica comando/estado
     │        │        ├─► Consulta database.py (Firebase)
     │        │        ├─► Llama ai_services.py (Gemini)
     │        │        └─► Envía respuesta via whatsapp_utils.py
     │        │
     │        └─► Actualiza Firebase
     │
     └─◄ Recibe respuesta en WhatsApp
```

---

## 🔧 Configuración Avanzada

### Personalizar Cursos

Edita `src/config/config.py` para agregar nuevos temas:

```python
CURSOS = {
    "java": {
        "nombre": "Java Fundamentals ☕",
        "lecciones": [
            "Variables y Primitivos", 
            "Operadores Lógicos", 
            "Condicionales (if-else)", 
            "Ciclos (for, while)", 
            "Arrays (Arreglos)",
            "Métodos y Funciones",
            "Clases y Objetos (OOP)"
        ]
    }
    # Agrega más lenguajes...
}
```

### Ajustar Gamificación

```python
# src/config/config.py
PUNTOS_POR_DIFICULTAD = {
    "Fácil": 10,
    "Intermedio": 20,
    "Difícil": 30
}

PUNTOS_PARA_NIVEL_UP = 100
```

### Crear Nuevos Logros

```python
# src/config/config.py - LOGROS_DISPONIBLES
"nuevo_logro": {
    "nombre": "Nombre del Logro",
    "descripcion": "Descripción",
    "emoji": "🏆",
    "requisito": {"retos_completados": 10},
    "puntos_bonus": 25
}
```

---

## 📊 Base de Datos (Firebase Firestore)

### Estructura de Documento de Usuario

```json
{
  "telefono": "1234567890",
  "nombre": "Luis",
  "nivel": "Intermedio",
  "puntos": 150,
  "nivel_general": 2,
  "onboarding_completado": true,
  "racha_dias": 5,
  "ultima_actividad": "2025-12-01",
  "estado_conversacional": "MENU_PRINCIPAL",
  "curso_actual": "Java",
  "leccion_actual": 3,
  "reto_actual": {
    "enunciado": "...",
    "solucion_ideal": "...",
    "tipo_reto": "Java",
    "dificultad": "Intermedio",
    "puntos": 20
  },
  "logros_desbloqueados": ["primer_paso", "aprendiz"],
  "fichas_desbloqueadas": ["java_variables", "java_loops"],
  "temas_completados": ["Variables", "Operadores"],
  "retos_completados": 8,
  "retos_fallados": 2,
  "historial_chat": [
    {"role": "user", "content": "Hola"},
    {"role": "assistant", "content": "¡Bienvenido!"}
  ]
}
```

### Operaciones CRUD

- **Crear**: `database.crear_usuario(telefono, nombre)`
- **Leer**: `database.obtener_usuario(telefono)`
- **Actualizar**: `database.actualizar_usuario(telefono, datos)`
- **Eliminar**: Gestión manual desde Firebase Console

---

## 🧪 Testing

### Verificar Configuración

```powershell
python -m src.scripts.verificar_config
```

### Test de Diagnóstico (Render)

```powershell
python -m src.scripts.diagnostico_render
```

### Pruebas Manuales

1. **Health Check**: `GET https://tu-app.onrender.com/`
2. **Webhook Verification**: `GET https://tu-app.onrender.com/webhook?hub.verify_token=TU_TOKEN&hub.challenge=test`

---

## 📚 API Reference

#### POST /webhook

**Request:**
```json
{
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "from": "1234567890",
          "text": {"body": "Hola"}
        }]
      }
    }]
  }]
}
```

**Response:**
```json
{
  "status": "ok"
}
```

#### GET /

**Health Check**

**Response:**
```json
{
  "status": "LogicBot activo",
  "version": "1.0.3",
  "uptime": "2h 34m"
}
```

---

## 🔧 Troubleshooting

> 📖 **Guía Completa**: Para más detalles sobre problemas de despliegue, consulta [RENDER_TROUBLESHOOTING.md](RENDER_TROUBLESHOOTING.md)

### Error: "ModuleNotFoundError: No module named 'main'" en Render

**Problema**: Render está ejecutando `main:app` en lugar de `src.main:app`

**Solución**:
1. Verifica que tu `Procfile` tenga:
   ```
   web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app
   ```
2. En el Dashboard de Render:
   - Ve a tu servicio
   - Settings → Build & Deploy
   - Haz clic en **"Clear build cache & deploy"**
3. Haz un commit y push para forzar un nuevo deploy:
   ```bash
   git commit --allow-empty -m "chore: trigger rebuild"
   git push origin main
   ```

### Error: Firebase Admin SDK no inicializa

**Solución**:
- Asegúrate de tener `firebase_credentials.json` en `src/config/`
- O configura las credenciales por defecto en Render/Google Cloud
- Verifica que el archivo no esté en `.gitignore` si lo necesitas en producción

### Error: Variables de entorno no cargadas

**Solución**:
1. Verifica que el archivo `.env` existe (local)
2. En Render: Settings → Environment → Add Environment Variable
3. Reinicia el servicio después de agregar variables

### El bot no responde en WhatsApp

**Solución**:
1. Verifica que el webhook esté configurado correctamente
2. Revisa los logs en Render Dashboard
3. Confirma que `VERIFY_TOKEN` sea el mismo en `.env` y Meta Dashboard
4. Verifica que el número de WhatsApp esté activo

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Sigue estos pasos:

### 1. Fork el Proyecto

```bash
git clone https://github.com/tu-usuario/Whatsapp-ChatBot-AI.git
cd Whatsapp-ChatBot-AI
```

### 2. Crea una Rama

```bash
git checkout -b feature/nueva-funcionalidad
```

### 3. Realiza tus Cambios

```bash
git add .
git commit -m "feat: descripción de la funcionalidad"
```

### 4. Push y Pull Request

```bash
git push origin feature/nueva-funcionalidad
```

### Convenciones de Commit

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `style:` Formato, sin cambios de código
- `refactor:` Refactorización
- `test:` Agregar/modificar tests
- `chore:` Tareas de mantenimiento

---

## 🐛 Reportar Problemas

Si encuentras un bug o tienes una sugerencia:

1. Ve a la pestaña [Issues](https://github.com/tu-usuario/Whatsapp-ChatBot-AI/issues)
2. Clic en **New Issue**
3. Usa la plantilla correspondiente:
   - 🐛 Bug Report
   - 💡 Feature Request
   - 📖 Documentation Update

---

## 🔐 Seguridad

### Buenas Prácticas Implementadas

- ✅ Variables de entorno para credenciales
- ✅ `.gitignore` configurado para excluir secretos
- ✅ Validación de tokens en webhook
- ✅ HTTPS obligatorio en producción
- ✅ Rate limiting en Render

### Archivos Sensibles (NO SUBIR A GIT)

```
.env
firebase_credentials.json
__pycache__/
*.pyc
```

### Reporte de Vulnerabilidades

Envía un correo a: **tu-email@example.com**

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

```
MIT License

Copyright (c) 2025 Luis Perez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 👨‍💻 Autor

**Luis Perez**

- GitHub: [@tu-usuario](https://github.com/tu-usuario)
- LinkedIn: [Tu Perfil](https://linkedin.com/in/tu-perfil)
- Email: tu-email@example.com

---

## 🙏 Agradecimientos

- **[Google Gemini AI](https://ai.google.dev/)** - Por la potencia de su IA
- **[Firebase](https://firebase.google.com/)** - Por la infraestructura de BD
- **[WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)** - Por la plataforma de mensajería
- **[FastAPI](https://fastapi.tiangolo.com/)** - Por el excelente framework
- **[Render](https://render.com/)** - Por el hosting gratuito

---

## 🗺️ Roadmap

### Versión 1.1 (Q1 2026)

- [ ] Soporte para Python como segundo lenguaje
- [ ] Sistema de grupos de estudio
- [ ] Exportar progreso a PDF
- [ ] Dashboard web de estadísticas

### Versión 1.2 (Q2 2026)

- [ ] Modo colaborativo (retos en parejas)
- [ ] Integración con GitHub para proyectos
- [ ] Sistema de mentores voluntarios
- [ ] Competencias semanales

### Versión 2.0 (Q3 2026)

- [ ] App móvil nativa complementaria
- [ ] Certificados de finalización
- [ ] Marketplace de retos comunitarios
- [ ] Soporte multiidioma (inglés, portugués)

---

## 📞 Soporte

### FAQ

**Q: ¿El bot es gratuito?**
A: Sí, totalmente gratuito y open source.

**Q: ¿Qué pasa si la IA no está disponible?**
A: El bot mostrará un mensaje de error y ofrecerá retos estáticos predefinidos.

**Q: ¿Puedo usar otro modelo de IA?**
A: Sí, puedes modificar `ai_services.py` para usar OpenAI, Claude, etc.

**Q: ¿Los datos de los usuarios están seguros?**
A: Sí, se almacenan encriptados en Firebase con reglas de seguridad.

### Contacto

- **Issues**: [GitHub Issues](https://github.com/tu-usuario/Whatsapp-ChatBot-AI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tu-usuario/Whatsapp-ChatBot-AI/discussions)
- **Email**: support@logicbot.dev

---

## ⭐ Agradece con una Estrella

Si este proyecto te fue útil, considera darle una ⭐ en GitHub. ¡Ayuda a otros desarrolladores a descubrirlo!

---

<div align="center">

**Desarrollado con ❤️ por Luis Perez**

[⬆ Volver arriba](#-logicbot---chatbot-educativo-de-programación)

</div>
