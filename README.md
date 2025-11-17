# 🤖 LogicBot - Tutor de Programación IA para WhatsApp

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Google Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Un chatbot educativo inteligente que enseña programación en Java a través de WhatsApp** 📱🎓

[Características](#-características) •
[Instalación](#-instalación) •
[Uso](#-uso) •
[Despliegue](#-despliegue) •
[Contribuir](#-contribuir)

</div>

---

## 📖 Descripción

**LogicBot** es un tutor de programación basado en IA que utiliza **Google Gemini 2.0 Flash** para:
- ✅ Generar retos de programación personalizados
- ✅ Evaluar soluciones de código con retroalimentación inteligente
- ✅ Mantener conversaciones pedagógicas (método socrático)
- ✅ Gamificar el aprendizaje con niveles y rachas

El bot funciona completamente dentro de **WhatsApp**, sin necesidad de apps adicionales.

---

## 🌟 Características

### 🎯 Sistema de Aprendizaje
- **7 Temas de Java:** Variables, Operadores, Condicionales, Ciclos, Arrays, Métodos, OOP
- **3 Niveles de Dificultad:** Fácil, Intermedio, Difícil
- **Retos Personalizados:** Generados por IA según tu nivel
- **Ayuda Inteligente:** Ofrece pistas sin dar la solución completa
- **Evaluación Automática:** Analiza tu código y da feedback constructivo

### 🎮 Gamificación
- **Sistema de Puntos:** Gana puntos según la dificultad del reto
- **Doble Nivel:**
  - Nivel General (experiencia global)
  - Nivel por Habilidad (progreso en cada tema)
- **Racha de Días:** Bonus por uso diario consecutivo
- **Perfil de Usuario:** Estadísticas detalladas de tu progreso

### 💬 Interacción Natural
- **Menús Interactivos:** Botones y listas dentro de WhatsApp
- **Chat Conversacional:** Haz preguntas sobre teoría
- **Comandos Rápidos:** `menu`, `me rindo`, `mi perfil`
- **Estado Persistente:** El bot recuerda tu progreso

---

## 🚀 Instalación

### Requisitos Previos
- **Python 3.11+**
- **PostgreSQL 15+**
- **Cuenta de WhatsApp Business API** ([Tutorial de configuración](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started))
- **API Key de Google Gemini** ([Obtener aquí](https://aistudio.google.com/app/apikey))

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/whatsapp-chatbot-ai.git
cd whatsapp-chatbot-ai
```

### Paso 2: Crear Entorno Virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### Paso 3: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Configurar Variables de Entorno
```bash
# Copiar plantilla
cp .env.example .env

# Editar .env con tus valores reales
# DATABASE_URL, WHATSAPP_TOKEN, ID_NUMERO_TELEFONO, GEMINI_API_KEY, VERIFY_TOKEN
```

### Paso 5: Inicializar Base de Datos
La base de datos se crea automáticamente al iniciar la app. Asegúrate de que PostgreSQL esté corriendo.

### Paso 6: Ejecutar Localmente
```bash
# Modo desarrollo con recarga automática
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: `http://localhost:8000`

---

## 🔧 Configuración de Webhook

### 1. Exponer el Servidor Local (para pruebas)
```bash
# Usando ngrok (recomendado para desarrollo)
ngrok http 8000
```

Obtendrás una URL pública como: `https://abc123.ngrok.io`

### 2. Configurar en Meta Developers
1. Ve a: [Meta Developers Console](https://developers.facebook.com/apps/)
2. Selecciona tu app > WhatsApp > Configuración
3. En **Webhook**, haz clic en "Configurar"
4. **URL del webhook:** `https://tu-dominio.com/webhook`
5. **Token de verificación:** El valor de `VERIFY_TOKEN` de tu `.env`
6. **Suscripciones:** Activa `messages`

### 3. Verificar Conexión
Envía un mensaje a tu número de WhatsApp Business desde cualquier contacto.

---

## 📱 Uso

### Iniciar Conversación
1. Abre WhatsApp y envía cualquier mensaje al número del bot
2. Recibirás un mensaje de bienvenida con un botón
3. Haz clic en **"Ver Menú Principal"**

### Menú Principal
```
🚀 Ruta de Aprendizaje
   ☕ Empezar Curso de Java → Elige un tema específico

💪 Práctica Libre
   🎲 Pedir Reto de Java → Reto aleatorio con dificultad personalizada

📊 Mi Progreso
   👤 Ver Mi Perfil → Estadísticas y niveles
```

### Comandos Disponibles
- `menu` - Volver al menú principal
- `me rindo` - Ver la solución del reto actual
- `mi perfil` - Ver tus estadísticas

### Flujo de Aprendizaje
```
1. Selecciona un tema (ej: "Ciclos (for, while)")
   ↓
2. Recibe un reto personalizado
   ↓
3. Envía tu solución en código Java
   ↓
4. Obtén feedback instantáneo
   ↓
5. Gana puntos y sube de nivel ⭐
```

---

## 🛠️ Tecnologías Utilizadas

| Categoría | Tecnología | Propósito |
|-----------|-----------|-----------|
| **Backend** | FastAPI | Servidor web asíncrono |
| **Base de Datos** | PostgreSQL + SQLAlchemy | Persistencia de usuarios y progreso |
| **IA** | Google Gemini 2.0 Flash | Generación de retos y evaluación |
| **Mensajería** | WhatsApp Business API | Canal de comunicación |
| **Deployment** | Gunicorn + Uvicorn | Servidor de producción |

---

## 📁 Estructura del Proyecto

```
whatsapp-chatbot-ai/
│
├── main.py                 # 🚪 Punto de entrada (FastAPI)
├── message_handler.py      # 🧠 Lógica conversacional
├── database.py            # 💾 Modelos y CRUD de PostgreSQL
├── ai_services.py         # 🤖 Integración con Gemini AI
├── whatsapp_utils.py      # 📱 Funciones de WhatsApp API
├── config.py              # ⚙️ Constantes y configuración
├── requirements.txt       # 📦 Dependencias
├── Procfile              # 🚀 Configuración de Heroku/Railway
├── .env.example          # 📝 Plantilla de variables de entorno
└── README.md             # 📖 Este archivo
```

---

## 🌐 Despliegue en Producción

### Opción 1: Railway (Recomendado)
1. Crea cuenta en [Railway.app](https://railway.app)
2. Conecta tu repositorio de GitHub
3. Agrega servicio PostgreSQL
4. Configura variables de entorno
5. Deploy automático ✅

### Opción 2: Heroku
```bash
# Instalar Heroku CLI
heroku login
heroku create nombre-de-tu-app

# Agregar PostgreSQL
heroku addons:create heroku-postgresql:mini

# Configurar variables
heroku config:set WHATSAPP_TOKEN=tu_token
heroku config:set GEMINI_API_KEY=tu_api_key
# ... (todas las variables del .env)

# Desplegar
git push heroku main
```

### Opción 3: Render
1. Crea cuenta en [Render.com](https://render.com)
2. New > Web Service
3. Conecta repositorio
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`
6. Agrega PostgreSQL desde Dashboard
7. Configura variables de entorno

---

## 🧪 Testing

```bash
# Ejecutar tests (cuando estén disponibles)
pytest tests/

# Verificar webhook manualmente
curl -X GET "http://localhost:8000/webhook?hub.mode=subscribe&hub.verify_token=micodigosecreto&hub.challenge=1234"
# Debería devolver: 1234
```

---

## 📊 Roadmap

### ✅ Versión 1.0 (Actual)
- [x] Sistema de retos con IA
- [x] Gamificación básica
- [x] 7 temas de Java
- [x] Menús interactivos de WhatsApp

### 🚧 Versión 2.0 (En Progreso)
- [ ] Soporte para Python
- [ ] Sistema de logros/badges
- [ ] Dashboard web para estadísticas
- [ ] Modo competitivo (rankings)

### 🔮 Versión 3.0 (Futuro)
- [ ] IA personalizada según estilo de aprendizaje
- [ ] Generación de certificados
- [ ] Comunidad/foro integrado
- [ ] Integración con LeetCode/HackerRank

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! 🎉

1. **Fork** el proyecto
2. Crea una **rama** para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add: nueva funcionalidad increíble'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. Abre un **Pull Request**

### Guías de Contribución
- Sigue el estilo de código existente (PEP 8)
- Añade docstrings a funciones nuevas
- Actualiza el README si es necesario
- Prueba tu código antes de enviar

---

## 🐛 Reporte de Bugs

Si encuentras un bug, por favor abre un [Issue](https://github.com/tu-usuario/whatsapp-chatbot-ai/issues) con:
- **Descripción** del problema
- **Pasos** para reproducirlo
- **Comportamiento esperado** vs **real**
- **Capturas** (si aplica)

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 👨‍💻 Autor

**Tu Nombre**
- GitHub: [@tu-usuario](https://github.com/tu-usuario)
- LinkedIn: [Tu Perfil](https://linkedin.com/in/tu-perfil)
- Email: tu.email@ejemplo.com

---

## 🙏 Agradecimientos

- [Google Gemini](https://deepmind.google/technologies/gemini/) - Por la API de IA
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp) - Por la plataforma de mensajería
- [FastAPI](https://fastapi.tiangolo.com/) - Por el excelente framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Por el ORM robusto

---

## ⭐ Si te gustó este proyecto, dale una estrella en GitHub!

<div align="center">

**Hecho con ❤️ y ☕ por la comunidad de desarrolladores**

[⬆ Volver arriba](#-logicbot---tutor-de-programación-ia-para-whatsapp)

</div>

