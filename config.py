# config.py

# Umbral de fallos antes de ofrecer ayuda teórica
UMBRAL_DE_FALLOS = 2

# Puntos otorgados por nivel de dificultad
PUNTOS_POR_DIFICULTAD = {
    "Fácil": 10,
    "Intermedio": 20,
    "Difícil": 30
}

# Puntos necesarios para subir de nivel
PUNTOS_PARA_NIVEL_UP = 100 

# Definición de cursos y rutas de aprendizaje
CURSOS = {
    "python": {
        "nombre": "Python Essentials 🐍",
        "lecciones": ["Variables y Tipos de Datos", "Operadores Aritméticos", "Condicionales (if/else)", "Bucles (for y while)", "Funciones"]
    },
    "java": {
        "nombre": "Java Fundamentals ☕",
        "lecciones": ["Sintaxis Básica", "Variables y Tipos Primitivos", "Operadores", "Clases y Objetos", "Métodos"]
    },
    "pseudocodigo": {
        "nombre": "Lógica con Pseudocódigo 🧠",
        "lecciones": ["Algoritmos y Diagramas de Flujo", "Variables y Constantes", "Estructuras Condicionales", "Estructuras Repetitivas", "Funciones y Procedimientos"]
    }
}