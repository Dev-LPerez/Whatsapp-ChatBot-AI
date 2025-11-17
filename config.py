# config.py

# Umbral de fallos antes de ofrecer ayuda teórica
UMBRAL_DE_FALLOS = 2

# Puntos otorgados por nivel de dificultad
PUNTOS_POR_DIFICULTAD = {
    "Fácil": 10,
    "Intermedio": 20,
    "Difícil": 30
}

# Puntos necesarios para subir de nivel GENERAL
PUNTOS_PARA_NIVEL_UP = 100 

# NUEVO: Puntos necesarios para subir de nivel en una HABILIDAD específica
PUNTOS_HABILIDAD_PARA_NIVEL_UP = 50

# Nombres de niveles generales
NOMBRES_NIVELES = {
    1: "Aprendiz 🌱",
    2: "Practicante 🔨",
    3: "Competente 💪",
    4: "Experto 🎯",
    5: "Maestro 🧙‍♂️",
    6: "Leyenda ⭐"
}

# Sistema de logros
LOGROS_DISPONIBLES = {
    "primer_paso": {
        "nombre": "Primer Paso",
        "descripcion": "Completaste el onboarding",
        "emoji": "🎯",
        "puntos_bonus": 5
    },
    "aprendiz": {
        "nombre": "Aprendiz",
        "descripcion": "Completaste 5 retos",
        "emoji": "📚",
        "requisito": {"retos_completados": 5},
        "puntos_bonus": 10
    },
    "consistente": {
        "nombre": "Consistente",
        "descripcion": "Mantuviste una racha de 3 días",
        "emoji": "🔥",
        "requisito": {"racha_dias": 3},
        "puntos_bonus": 15
    },
    "dedicado": {
        "nombre": "Dedicado",
        "descripcion": "Mantuviste una racha de 7 días",
        "emoji": "💪",
        "requisito": {"racha_dias": 7},
        "puntos_bonus": 30
    },
    "perfeccionista": {
        "nombre": "Perfeccionista",
        "descripcion": "Resolviste 10 retos sin pedir pistas",
        "emoji": "💎",
        "requisito": {"retos_sin_pistas": 10},
        "puntos_bonus": 25
    },
    "maestro_variables": {
        "nombre": "Maestro de Variables",
        "descripcion": "Alcanzaste nivel 3 en Variables",
        "emoji": "⚡",
        "requisito": {"tema": "Variables y Primitivos", "nivel": 3},
        "puntos_bonus": 20
    },
    "imparable": {
        "nombre": "Imparable",
        "descripcion": "Completaste 50 retos",
        "emoji": "🚀",
        "requisito": {"retos_completados": 50},
        "puntos_bonus": 50
    }
}

# Definición del curso de Java con lecciones específicas
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
}