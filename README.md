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

### 💬 Interfaz Interactiva

- **Menús Nativos de WhatsApp**: Listas y botones interactivos
- **Navegación Intuitiva**: Comandos simples y guiados
- **Mensajes Personalizados**: Emojis y formato adaptado a WhatsApp
- **Historial Contextual**: Recuerda tus últimas 6 interacciones

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

> **Nota**: Para ver ejemplos visuales, consulta la carpeta `/docs`

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

Crea un archivo `.env` en la raíz del proyecto:

```env
# WhatsApp Business API
WHATSAPP_TOKEN=tu_token_de_whatsapp
VERIFY_TOKEN=tu_token_de_verificacion
WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id

# Google Gemini AI
GEMINI_API_KEY=tu_api_key_de_gemini

# Firebase (opcional si usas archivo JSON)
# GOOGLE_APPLICATION_CREDENTIALS=firebase_credentials.json

# Configuración del Servidor
PORT=8000
```

### 5️⃣ Configurar Firebase

**Opción 1: Usando archivo de credenciales (Recomendado para desarrollo local)**

Descarga tu archivo de credenciales desde la consola de Firebase:

**Pasos:**
1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto
3. Ve a **Configuración del Proyecto** > **Cuentas de Servicio**
4. Clic en **Generar nueva clave privada**
5. Guarda el archivo como `firebase_credentials.json` en la raíz del proyecto

**⚠️ IMPORTANTE: Este archivo contiene credenciales sensibles**
- **NUNCA** lo subas a Git (ya está en `.gitignore`)
- Usa `firebase_credentials.json.example` como referencia
- En producción, usa variables de entorno

**Opción 2: Usando variables de entorno (Recomendado para producción)**

```env
GOOGLE_APPLICATION_CREDENTIALS=firebase_credentials.json
# O configura las credenciales directamente como variables de entorno
```

### 6️⃣ Verificar Configuración

```powershell
python verificar_config.py
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
uvicorn main:app --reload --port 8000
```

El servidor estará disponible en `http://localhost:8000`

### Modo Producción (Render)

El proyecto incluye configuración automática para Render:

1. **Archivo `Procfile`**: Define el comando de inicio
2. **Script `build.sh`**: Instalación de dependencias
3. **Variables de Entorno**: Configuradas en Render Dashboard

**Despliegue automático** al hacer push a la rama `main`

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
├── main.py                    # Punto de entrada (FastAPI)
├── config.py                  # Configuración global
├── database.py                # Lógica de Firebase
├── ai_services.py             # Integración con Gemini AI
├── message_handler.py         # Enrutamiento de mensajes
├── whatsapp_utils.py          # Funciones de WhatsApp API
├── keep_alive.py              # Health check para Render
├── verificar_config.py        # Script de diagnóstico
├── requirements.txt           # Dependencias Python
├── Procfile                   # Config para Render
├── build.sh                   # Script de build
├── firebase_credentials.json  # Credenciales Firebase (no subir a Git)
│
├── message_components/        # Componentes modulares
│   ├── __init__.py
│   ├── onboarding.py         # Flujo de bienvenida
│   └── achievements.py       # Sistema de logros
│
└── utils/                     # Utilidades
    ├── __init__.py
    ├── emojis.py             # Constantes de emojis
    └── formatters.py         # Formateadores de texto
```
    ├── REQUERIMIENTOS.md     # Especificación funcional
    ├── RENDER_DEPLOY.md      # Guía de despliegue
    ├── MEJORAS_UX_IMPLEMENTADAS.md
    └── CASOS_DE_USO.puml     # Diagramas UML
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

Edita `config.py` para agregar nuevos temas:

```python
CURSOS = {
    "Java": {
        "temas": [
            {"id": "1", "nombre": "Variables y Tipos de Datos"},
            {"id": "2", "nombre": "Operadores"},
            # Agrega más temas...
        ]
    },
    # Agrega más lenguajes...
}
```

### Ajustar Gamificación

```python
# config.py
PUNTOS_POR_DIFICULTAD = {
    "Fácil": 10,
    "Intermedio": 20,
    "Difícil": 30
}

PUNTOS_PARA_NIVEL_UP = 100
```

### Crear Nuevos Logros

```python
# config.py - LOGROS_DISPONIBLES
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
python verificar_config.py
```

### Test de Diagnóstico (Render)

```powershell
python diagnostico_render.py
```

### Pruebas Manuales

1. **Health Check**: `GET https://tu-app.onrender.com/`
2. **Webhook Verification**: `GET https://tu-app.onrender.com/webhook?hub.verify_token=TU_TOKEN&hub.challenge=test`

---

## 📚 Documentación

### Guías Disponibles

- **[GUIA_INICIO.md](docs/GUIA_INICIO.md)** - Configuración paso a paso
- **[REQUERIMIENTOS.md](docs/REQUERIMIENTOS.md)** - Especificación funcional completa
- **[RENDER_DEPLOY.md](docs/RENDER_DEPLOY.md)** - Despliegue en producción
- **[MEJORAS_UX_IMPLEMENTADAS.md](docs/MEJORAS_UX_IMPLEMENTADAS.md)** - Changelog de UX
- **[CASOS_DE_USO.puml](docs/CASOS_DE_USO.puml)** - Diagramas UML

### API Reference

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

