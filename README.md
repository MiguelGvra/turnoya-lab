# TurnoYa Lab — Sistema de Agendamiento Académico

¡Bienvenido al laboratorio práctico de calidad de software! **TurnoYa Lab** es un mini sistema de agendamiento diseñado intencionalmente con múltiples fallas funcionales, de rendimiento, usabilidad y mantenibilidad bajo el estándar **ISO/IEC 25010**. Tu objetivo será auditarla, medir sus problemas e implementar las refactorizaciones.

##  Mapa de Fallas Intencionales
- **RF01:** Permite guardar clientes sin número telefónico (Usabilidad / Confiabilidad).
- **RF02:** Catálogo de servicios estático bloqueado en el código (Mantenibilidad).
- **RF03:** Permite registrar múltiples citas idénticas para el mismo cliente a la misma hora (Confiabilidad).
- **RF04:** La pestaña de agenda se ralentiza artificialmente según volumen (Eficiencia de Desempeño).

## Instrucciones de Ejecución Local
1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt