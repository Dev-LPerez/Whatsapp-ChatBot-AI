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

# Definición del curso de Java con lecciones específicas
CURSOS = {
    "java": {
        "nombre": "Java Fundamentals ☕",
        "lecciones": [
            "Variables y Tipos Primitivos", 
            "Operadores Aritméticos y Lógicos", 
            "Condicionales (if-else, switch)", 
            "Ciclos (for, while, do-while)", 
            "Arrays (Arreglos)",
            "Métodos y Funciones",
            "Conceptos Básicos de Clases y Objetos"
        ]
    }
}