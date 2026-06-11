## Resumen

<!-- Describe brevemente qué cambia y por qué. -->


## Alcance del cambio

- [ ] No modifica `app/` salvo justificación explícita en este PR.
- [ ] No habilita `real`.
- [ ] No habilita `test_keys`.
- [ ] No agrega ejecución real de teclas.
- [ ] No agrega grabación de macros.
- [ ] No agrega mouse, clicks ni movimientos.
- [ ] Actualiza documentación si aplica.

## Justificación si modifica `app/`

<!-- Si no modifica app/, escribe "No aplica". Si modifica app/, explica por qué es necesario y cómo mantiene el alcance seguro. -->


## Pruebas locales

- [ ] Pasa `python -m compileall app`.
- [ ] Pasa `python -m unittest discover -s tests`.
- [ ] Pasa la verificación estática sin pulsaciones reales:

```powershell
python -c "from pathlib import Path; text=Path('app/ui.py').read_text(encoding='utf-8') + Path('app/macro_runner.py').read_text(encoding='utf-8'); forbidden=['Controller(', '.press(', '.release(']; print(all(item not in text for item in forbidden)); raise SystemExit(0 if all(item not in text for item in forbidden) else 1)"
```

## Notas para revisión

<!-- Agrega riesgos, decisiones o puntos que conviene revisar con cuidado. -->
