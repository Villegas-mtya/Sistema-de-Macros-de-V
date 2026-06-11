# Política de seguridad

## Versiones soportadas actualmente

| Versión | Estado | Soporte de seguridad |
| --- | --- | --- |
| `v0.1.0-rc1` | Release candidate pública/manual | Soportada para reportes de seguridad y feedback reproducible |
| Versiones anteriores | No publicadas como release candidate | No soportadas |

`v0.1.0-rc1` es una release candidate segura: sirve para revisión pública, pruebas manuales y reportes ordenados sin habilitar automatización real.

## Alcance seguro de la release candidate

La aplicación mantiene límites estrictos de seguridad:

- `real` sigue bloqueado.
- `test_keys` sigue bloqueado.
- No hay ejecución real de teclas.
- No hay grabación de macros.
- No hay captura de teclado para construir acciones automáticamente.
- No hay mouse.
- No hay clicks.
- No hay movimientos de mouse.

Cualquier reporte, propuesta o contribución debe respetar este alcance. No se aceptan solicitudes para evasión, ocultamiento, bypass, ejecución no autorizada, automatización abusiva o comportamiento destinado a eludir controles de seguridad.

## Cómo reportar vulnerabilidades o problemas de seguridad

Para reportar un problema de seguridad, usa la plantilla **Security report** en GitHub Issues si el contenido puede compartirse públicamente sin exponer secretos, datos sensibles o instrucciones abusivas.

Si el reporte incluye información sensible, no publiques secretos, tokens, credenciales, datos personales ni detalles explotables innecesarios en un issue público. En ese caso, abre un reporte mínimo indicando que existe un problema de seguridad y evita incluir datos privados.

## Información útil en un reporte de seguridad

Incluye, siempre que sea seguro hacerlo:

1. Versión afectada, por ejemplo `v0.1.0-rc1`.
2. Sistema operativo y forma de ejecución: Python o `.exe`.
3. Descripción clara del riesgo observado.
4. Pasos seguros para reproducir el problema sin presionar teclas reales ni activar comportamientos fuera de alcance.
5. Impacto esperado si el problema no se corrige.
6. Logs, capturas o mensajes de error solo si no contienen datos sensibles.
7. Confirmación de que el reporte no solicita evasión, ocultamiento, bypass, ejecución no autorizada ni uso abusivo.

## Límites para reportes y contribuciones

No se aceptarán reportes ni cambios que pidan o implementen:

- Habilitar `real`.
- Habilitar `test_keys`.
- Ejecutar teclas reales.
- Grabar macros.
- Capturar teclado para automatización.
- Automatizar mouse, clicks o movimientos.
- Evadir restricciones de aplicaciones, juegos, sistemas operativos o servicios.
- Ocultar automatización o evitar detección.
- Bypasses, ejecución no autorizada o comportamiento abusivo.

La Fase 19 solo prepara el repositorio para recibir feedback y reportes de seguridad de forma ordenada. No cambia el comportamiento funcional de la aplicación.
