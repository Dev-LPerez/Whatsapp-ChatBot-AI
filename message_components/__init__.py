# message_components/__init__.py
# Módulo de componentes de mensajería

from .onboarding import (
    iniciar_onboarding,
    handle_onboarding_paso_1,
    handle_onboarding_paso_2,
    completar_onboarding,
    finalizar_onboarding_y_empezar
)

from .achievements import (
    verificar_y_otorgar_logros,
    mostrar_logros_usuario
)

__all__ = [
    'iniciar_onboarding',
    'handle_onboarding_paso_1',
    'handle_onboarding_paso_2',
    'completar_onboarding',
    'finalizar_onboarding_y_empezar',
    'verificar_y_otorgar_logros',
    'mostrar_logros_usuario'
]

