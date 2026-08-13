"""Generacion de PDF LaTeX sin dependencias de Streamlit o Telegram."""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = PACKAGE_DIR / "plantilla.tex"


def formato_clp(valor) -> str:
    try:
        return f"${valor:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "$0"


def _escape_latex(text):
    text = str(text)
    for char, escaped in [
        ("&", "\\&"), ("%", "\\%"), ("$", "\\$"), ("#", "\\#"),
        ("_", "\\_"), ("{", "\\{"), ("}", "\\}"),
        ("~", "\\textasciitilde{}"), ("^", "\\textasciicircum{}"),
    ]:
        text = text.replace(char, escaped)
    return text


def build_latex(project_title, project_header, cart_items, service_items, totals):
    """Construye el texto LaTeX sin compilarlo, para permitir pruebas directas."""
    tex = TEMPLATE_PATH.read_text(encoding="utf-8")

    def clp(value):
        return formato_clp(value).replace("$", "")

    if cart_items:
        filas = []
        for item in cart_items:
            filas.append(
                f"{_escape_latex(item['nombre'])} & {item['cantidad']} & "
                f"{clp(item['precio_unitario'])} & "
                f"{clp(item['cantidad'] * item['precio_unitario'])} \\\\")
        tex = tex.replace("\nBLOCK_MATERIALES\n", "\n" + "\n".join(filas) + "\n")
    else:
        tex = re.sub(
            r"%% BLOCK_MATERIALES_SECTION %%.*?%% END_MATERIALES_SECTION %%",
            "", tex, flags=re.DOTALL,
        )

    if service_items:
        filas = []
        for service in service_items:
            filas.append(
                f"{_escape_latex(service['nombre'])} & {clp(service['valor'])} \\\\")
        tex = tex.replace("\nBLOCK_SERVICIOS\n", "\n" + "\n".join(filas) + "\n")
    else:
        tex = re.sub(
            r"%% BLOCK_SERVICIOS_SECTION %%.*?%% END_SERVICIOS_SECTION %%",
            "", tex, flags=re.DOTALL,
        )

    if totals["descuento"] > 0:
        tex = tex.replace("DESCUENTO_LABEL", "Descuento")
        tex = tex.replace("TOTAL_DESCUENTO", clp(totals["descuento"]))
    else:
        tex = re.sub(
            r"%% BLOCK_DESCUENTO_ROW %%.*?%% END_DESCUENTO_ROW %%",
            "", tex, flags=re.DOTALL,
        )

    tex = tex.replace("HEADER_PROYECTO", _escape_latex(project_header or ""))
    tex = tex.replace(
        "TITULO_PROYECTO",
        _escape_latex((project_title or "PRESUPUESTO").upper()),
    )
    tex = tex.replace("TOTAL_MATERIALES", clp(totals["total_materiales"]))
    tex = tex.replace("TOTAL_SERVICIOS", clp(totals["total_servicios"]))
    tex = tex.replace("SUBTOTAL_GENERAL", clp(totals["subtotal"]))
    tex = tex.replace("TOTAL_GENERAL", clp(totals["total_final"]))
    return tex


def generate_pdf(project_title, project_header, cart_items, service_items, totals):
    """Compila la plantilla canonica con pdflatex y devuelve bytes PDF."""
    if shutil.which("pdflatex") is None:
        raise RuntimeError("No se encontro pdflatex en este entorno.")

    tex = build_latex(project_title, project_header, cart_items, service_items, totals)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        tex_path = tmp_path / "presupuesto.tex"
        tex_path.write_text(tex, encoding="utf-8")

        for _ in range(2):
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
                cwd=tmpdir,
                capture_output=True,
                check=False,
            )

        pdf_path = tmp_path / "presupuesto.pdf"
        if pdf_path.exists():
            return pdf_path.read_bytes()
    raise RuntimeError("pdflatex no pudo generar el PDF.")
