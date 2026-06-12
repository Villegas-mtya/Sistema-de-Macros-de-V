# Roadmap público y estado del proyecto

Este documento describe el estado actual de **Sistema de Macros de V**, las fases ya completadas, las ideas pendientes que pueden evaluarse dentro del alcance seguro y los límites que no deben cruzarse sin una fase específica, revisión de seguridad y aprobación manual.

## Estado actual del proyecto

- **Versión actual:** `v0.1.0-rc1`.
- **Tipo de versión:** release candidate segura publicada manualmente como pre-release.
- **Distribución actual:** artifact Windows generado por el workflow manual `release-build` y adjuntado manualmente a la pre-release.
- **Modos de ejecución permitidos:** `test_log` por defecto y `real` solo con selección explícita y confirmación manual.
- **Modo bloqueado:** `test_keys` sigue bloqueado/no implementado.
- **Ejecución real de teclas:** implementada de forma controlada para teclado en Fase 22, sin grabación ni mouse.
- **Grabación:** no existe grabación de macros ni captura de teclado para construir acciones.
- **Mouse:** no hay soporte para mouse, clicks ni movimientos.
- **Alcance de Fase 22:** ejecución real controlada de teclado, selector `test_log`/`real`, confirmación manual y pruebas con controlador falso.

La aplicación actual permite construir macros manuales, validarlas, guardarlas como JSON, previsualizarlas y ejecutarlas en `test_log` o en `real`. `test_log` solo registra eventos; `real` presiona teclas reales de teclado después de selección explícita y confirmación visual.

## Completado

Las fases completadas dejaron una base segura, verificable y documentada:

- Estructura base del proyecto Python y punto de entrada de la aplicación.
- Rutas seguras para datos de usuario, configuración, macros y logs.
- Mapeo de teclas con nombres visibles y valores internos estables.
- Validación de teclas simples y avanzadas antes de guardar o ejecutar una macro.
- Almacenamiento JSON de macros con carga, listado, borrado, importación y exportación.
- Previsualización declarativa de macros antes de ejecutar, incluyendo repeticiones, delays y duración estimada.
- Runner con `test_log` seguro y modo `real` controlado mediante controlador de teclado inyectable/testeable.
- Parada de emergencia F9 limitada al runner seguro.
- UI manual para construir macros sin grabación automática.
- Edición visual de acciones existentes.
- Reordenamiento, duplicación y eliminación de acciones desde la UI.
- Guardado, carga, importación y exportación de macros desde la UI.
- Build preliminar con PyInstaller para Windows sin habilitar ejecución real.
- Pruebas automatizadas con `unittest` para regresión y seguridad estática.
- CI automático en GitHub Actions para validar el proyecto sin abrir la UI ni ejecutar el `.exe`.
- Workflow manual `release-build` para generar artifact Windows bajo revisión manual.
- Release candidate pública/manual `v0.1.0-rc1`.
- `SECURITY.md` con política de seguridad, versiones soportadas y límites de reportes.
- Plantillas de issues para bugs, feedback de release candidate y reportes de seguridad.
- Plantilla de pull request con checklist de alcance seguro.
- Guía de usuario final en `docs/USER_GUIDE.md`.
- Guía de solución de problemas en `docs/TROUBLESHOOTING.md`.

## Pendiente seguro

Las siguientes ideas pueden evaluarse en futuras fases siempre que no cambien el comportamiento funcional seguro ni habiliten ejecución real:

- Mejorar y ampliar la documentación pública del proyecto.
- Agregar más ejemplos JSON seguros para pruebas manuales y documentación.
- Agregar capturas de pantalla a la guía de usuario.
- Mejorar el checklist de QA manual para release candidates.
- Agregar más pruebas unitarias documentales o estáticas.
- Mejorar mensajes de error sin cambiar el comportamiento de validación ni ejecución.
- Revisar accesibilidad de la UI: textos, contraste, orden visual y claridad de botones.
- Revisar el empaquetado Windows y documentar una posible firma futura del ejecutable si aplica.
- Mejorar la trazabilidad documental entre README, changelog, checklist, seguridad y roadmap.
- Revisar ejemplos de reportes reproducibles para facilitar feedback público.

Estas tareas son aceptables solo si conservan el límite principal: `test_log` sigue disponible por defecto y `real` requiere selección explícita y confirmación manual.

## Fuera del alcance actual

No está implementado ni autorizado:

- Modo `test_keys`.
- Ejecución real sin confirmación visual.
- Ejecución automática o no autorizada.
- Grabación de macros.
- Captura de teclado para construir acciones automáticamente.
- Soporte de mouse.
- Clicks.
- Movimientos de mouse.
- Evasión de restricciones.
- Ocultamiento del comportamiento de la aplicación.
- Bypass de controles, permisos o sistemas externos.
- Ejecución no autorizada.
- Comportamiento abusivo, engañoso o diseñado para operar sin consentimiento.

Cualquier propuesta que dependa de estos puntos debe rechazarse para el estado actual del proyecto.

## Límites de seguridad

Los límites de seguridad vigentes son obligatorios para revisiones, issues, pull requests y futuras fases:

- Mantener `execution_mode = "test_log"` como modo por defecto y `real` solo con confirmación manual.
- Mantener bloqueado `test_keys`.
- Permitir llamadas que presionen teclas reales únicamente dentro de `app/macro_runner.py`.
- No agregar grabación ni captura global para construir macros.
- No agregar mouse, clicks ni movimientos.
- No agregar automatización de publicación de releases sin revisión manual.
- No debilitar validaciones existentes de macros, teclas, delays, repeticiones o modos de ejecución.
- No eliminar pruebas de seguridad ni documentación de límites sin reemplazo equivalente o más estricto.

## Criterios para aceptar futuras fases

Una fase futura solo debería aceptarse si cumple todos estos criterios:

1. Tiene una especificación explícita y acotada.
2. Incluye revisión de seguridad antes de implementar.
3. Define pruebas locales o automatizadas adecuadas para el cambio.
4. Actualiza la documentación afectada.
5. Requiere aprobación manual antes de integrarse.
6. No rompe límites existentes de seguridad, validación ni distribución.
7. No habilita ejecución real sin una fase específica, revisión formal y controles adicionales.
8. Mantiene compatibilidad con el alcance público documentado para `v0.1.0-rc1` salvo que una nueva fase aprobada indique lo contrario.
9. Evita dependencias nuevas salvo justificación explícita y revisión de impacto.
10. Permite una revisión clara del diff, sin mezclar cambios funcionales con cambios documentales no relacionados.

## Nota para Fase 23

Fase 22 no autoriza Fase 23. Antes de avanzar se necesita una nueva especificación explícita que indique objetivo, alcance, archivos permitidos, pruebas esperadas y revisión de seguridad.
