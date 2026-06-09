"""Utilidades iniciales de presentación para macros."""

VARIATION_LABELS = {
    "fixed": "Sin variación",
    "light": "Variación ligera",
    "medium": "Variación media",
    "high": "Variación alta",
}


def get_variation_label(variation_mode: str) -> str:
    """Devuelve el texto visible para una variación de tiempo."""
    return VARIATION_LABELS.get(variation_mode, "Variación desconocida")
