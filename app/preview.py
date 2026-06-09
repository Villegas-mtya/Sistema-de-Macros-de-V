"""Previsualización y estimación de duración de macros.

La Fase 5 trabaja únicamente con datos ya validados: no ejecuta teclas, no
activa atajos globales y no abre interfaces gráficas. El objetivo es construir
un resumen estructurado que una futura UI pueda mostrar antes de ejecutar una
macro.
"""

from __future__ import annotations

from typing import Any

from app.key_mapper import get_key_display_name
from app.validators import validate_macro_action, validate_macro_data

VARIATION_LABELS = {
    "fixed": "Sin variación",
    "light": "Variación ligera",
    "medium": "Variación media",
    "high": "Variación alta",
}

VARIATION_SECONDS = {
    "fixed": 0.0,
    "light": 0.15,
    "medium": 0.30,
    "high": 0.50,
}


DurationRange = dict[str, float]


def get_variation_label(variation_mode: str) -> str:
    """Devuelve el texto visible para una variación de tiempo."""
    return VARIATION_LABELS.get(variation_mode, "Variación desconocida")


def get_variation_seconds(variation_mode: str) -> float:
    """Devuelve cuántos segundos puede variar un modo de variación.

    La variación se aplica simétricamente sobre el retardo base: resta para el
    mínimo y suma para el máximo. Un modo desconocido se rechaza de inmediato
    para evitar previsualizaciones engañosas.
    """
    if variation_mode not in VARIATION_SECONDS:
        valid_modes = ", ".join(sorted(VARIATION_SECONDS))
        raise ValueError(
            f"Modo de variación inválido: {variation_mode!r}. "
            f"Modos válidos: {valid_modes}"
        )

    return VARIATION_SECONDS[variation_mode]


def calculate_delay_range(base_delay: object, variation_mode: str) -> DurationRange:
    """Calcula mínimo, promedio y máximo para un retardo con variación.

    Regla de Fase 5:
    - mínimo = max(0, base_delay - variation)
    - promedio = base_delay
    - máximo = base_delay + variation
    """
    delay = _to_non_negative_float(base_delay, "base_delay")
    variation = get_variation_seconds(variation_mode)

    return {
        "min": max(0.0, delay - variation),
        "avg": delay,
        "max": delay + variation,
    }


def estimate_macro_duration(macro_data: object) -> dict[str, Any]:
    """Estima la duración mínima, promedio y máxima de una macro validada.

    La estimación suma el retardo inicial una sola vez, los retardos de cada
    acción por repetición y el cooldown entre repeticiones. En macros infinitas
    el total no tiene fin, así que se informa ``total`` como ``None`` y se ofrece
    una referencia de duración por repetición y por ciclo repetible.
    """
    if not validate_macro_data(macro_data):
        raise ValueError("La macro no cumple la estructura válida para previsualizar")

    macro = macro_data
    actions = macro["actions"]
    infinite = macro["infinite"]
    repetitions = macro["repetitions"]

    initial_delay_range = _fixed_range(macro["initial_delay"], "initial_delay")
    per_repetition_range = _sum_ranges(
        calculate_delay_range(action["base_delay"], action["variation_mode"])
        for action in actions
    )
    cooldown_range = calculate_delay_range(
        macro["cooldown_base"], macro["cooldown_variation"]
    )

    if infinite:
        per_cycle_range = _add_ranges(per_repetition_range, cooldown_range)
        total_range = None
    else:
        total_range = _add_ranges(
            initial_delay_range,
            _multiply_range(per_repetition_range, repetitions),
        )

        if repetitions > 1:
            total_range = _add_ranges(
                total_range,
                _multiply_range(cooldown_range, repetitions - 1),
            )

        per_cycle_range = None

    return {
        "infinite": infinite,
        "repetitions": repetitions,
        "actions_count": len(actions),
        "initial_delay": initial_delay_range,
        "cooldown": cooldown_range,
        "total": total_range,
        "per_repetition": per_repetition_range,
        "per_cycle": per_cycle_range,
    }


def format_seconds(seconds: object) -> str:
    """Convierte segundos a texto legible para una UI futura.

    Los tiempos menores a un minuto conservan decimales útiles cuando existen.
    Para duraciones de un minuto o más se redondea al segundo más cercano y se
    muestra como horas, minutos y segundos.
    """
    total_seconds = _to_non_negative_float(seconds, "seconds")

    if total_seconds < 60:
        return f"{_format_number(total_seconds)} s"

    rounded_seconds = int(round(total_seconds))
    hours, remainder = divmod(rounded_seconds, 3600)
    minutes, seconds_left = divmod(remainder, 60)

    parts = []
    if hours:
        parts.append(f"{hours} h")
    if minutes:
        parts.append(f"{minutes} min")
    if seconds_left or not parts:
        parts.append(f"{seconds_left} s")

    return " ".join(parts)


def build_action_preview(action: object, index: int) -> dict[str, Any]:
    """Construye una previsualización estructurada de una acción.

    ``index`` es 1-based para mostrarse directamente en una tabla o lista de UI.
    """
    if not isinstance(index, int) or index < 1:
        raise ValueError("El índice de acción debe ser un entero mayor o igual a 1")

    if not validate_macro_action(action):
        raise ValueError(f"La acción {index} no cumple la estructura válida")

    delay_range = calculate_delay_range(action["base_delay"], action["variation_mode"])
    key_display_name = get_key_display_name(action["key"])

    return {
        "index": index,
        "key": action["key"],
        "key_display_name": key_display_name or str(action["key"]),
        "base_delay": float(action["base_delay"]),
        "variation_mode": action["variation_mode"],
        "delay_range": delay_range,
        "delay_range_text": _format_range_text(delay_range),
    }


def build_macro_preview(macro_data: object) -> dict[str, Any]:
    """Construye el resumen completo de una macro antes de ejecutarla.

    Esta función es deliberadamente declarativa: devuelve un ``dict`` serializable
    y legible para que una UI posterior pueda renderizarlo sin recalcular reglas.
    """
    if not validate_macro_data(macro_data):
        raise ValueError("La macro no cumple la estructura válida para previsualizar")

    macro = macro_data
    action_previews = [
        build_action_preview(action, index)
        for index, action in enumerate(macro["actions"], start=1)
    ]
    duration_estimate = estimate_macro_duration(macro)

    preview = {
        "app": macro["app"],
        "version": macro["version"],
        "actions": action_previews,
        "actions_count": len(action_previews),
        "initial_delay": float(macro["initial_delay"]),
        "repetitions": macro["repetitions"],
        "infinite": macro["infinite"],
        "cooldown_base": float(macro["cooldown_base"]),
        "cooldown_variation": macro["cooldown_variation"],
        "execution_mode": macro["execution_mode"],
        "key_selection_mode": macro["key_selection_mode"],
        "duration_estimate": duration_estimate,
    }
    preview["human_summary"] = _build_human_summary(preview)
    return preview


def _to_non_negative_float(value: object, field_name: str) -> float:
    """Convierte un valor numérico y rechaza booleanos, texto inválido y negativos."""
    if isinstance(value, bool):
        raise ValueError(f"{field_name} debe ser un número mayor o igual a cero")

    try:
        numeric_value = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"{field_name} debe ser un número mayor o igual a cero"
        ) from error

    if numeric_value < 0:
        raise ValueError(f"{field_name} no puede ser negativo")

    return numeric_value


def _fixed_range(value: object, field_name: str) -> DurationRange:
    """Crea un rango sin variación para retardos fijos como el initial_delay."""
    numeric_value = _to_non_negative_float(value, field_name)
    return {"min": numeric_value, "avg": numeric_value, "max": numeric_value}


def _sum_ranges(ranges: Any) -> DurationRange:
    """Suma una colección de rangos de duración."""
    total = {"min": 0.0, "avg": 0.0, "max": 0.0}
    for duration_range in ranges:
        total = _add_ranges(total, duration_range)
    return total


def _add_ranges(first: DurationRange, second: DurationRange) -> DurationRange:
    """Suma dos rangos manteniendo las claves mínimas, promedio y máximas."""
    return {
        "min": first["min"] + second["min"],
        "avg": first["avg"] + second["avg"],
        "max": first["max"] + second["max"],
    }


def _multiply_range(duration_range: DurationRange, multiplier: int) -> DurationRange:
    """Multiplica un rango por una cantidad entera de repeticiones."""
    return {
        "min": duration_range["min"] * multiplier,
        "avg": duration_range["avg"] * multiplier,
        "max": duration_range["max"] * multiplier,
    }


def _format_range_text(duration_range: DurationRange) -> str:
    """Devuelve un texto compacto para mostrar min/promedio/máximo."""
    return (
        f"mín {format_seconds(duration_range['min'])} / "
        f"prom {format_seconds(duration_range['avg'])} / "
        f"máx {format_seconds(duration_range['max'])}"
    )


def _format_number(value: float) -> str:
    """Formatea números evitando ceros decimales innecesarios."""
    if value.is_integer():
        return str(int(value))

    return f"{value:.2f}".rstrip("0").rstrip(".")


def _build_human_summary(preview: dict[str, Any]) -> list[str]:
    """Construye líneas de texto simples para una futura pantalla de resumen."""
    duration_estimate = preview["duration_estimate"]
    summary = [
        f"Acciones: {preview['actions_count']}",
        _format_repetitions_text(preview),
        f"Modo de ejecución: {preview['execution_mode']}",
        f"Modo de selección de teclas: {preview['key_selection_mode']}",
    ]

    if preview["infinite"]:
        summary.append("Duración estimada: indefinida")
        summary.append(
            "Duración por ciclo: "
            f"{_format_range_text(duration_estimate['per_cycle'])}"
        )
    else:
        summary.append(
            "Duración estimada: "
            f"{_format_range_text(duration_estimate['total'])}"
        )

    return summary


def _format_repetitions_text(preview: dict[str, Any]) -> str:
    """Devuelve una línea legible para repeticiones finitas o infinitas."""
    if preview["infinite"]:
        return "Repeticiones: infinitas"

    return f"Repeticiones: {preview['repetitions']}"


__all__ = [
    "get_variation_label",
    "get_variation_seconds",
    "calculate_delay_range",
    "estimate_macro_duration",
    "format_seconds",
    "build_action_preview",
    "build_macro_preview",
]
