"""Motor compartido de calculo y generacion de presupuestos KaZe."""

from .pdf import build_latex, generate_pdf, formato_clp
from .presupuesto import calculate_discount, calculate_totals, validar_descuento

__all__ = [
    "build_latex",
    "calculate_discount",
    "calculate_totals",
    "formato_clp",
    "generate_pdf",
    "validar_descuento",
]
