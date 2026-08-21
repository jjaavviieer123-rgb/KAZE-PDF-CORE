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


def _strip_block(tex, start_marker, end_marker):
    return re.sub(
        rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}",
        "",
        tex,
        flags=re.DOTALL,
    )


def build_latex(project_title, project_header, cart_items, service_items, totals, tipo_documento="detallado"):
    """Construye el texto LaTeX sin compilarlo, para permitir pruebas directas."""
    tex = TEMPLATE_PATH.read_text(encoding="utf-8")

    def clp(value):
        return formato_clp(value).replace("$", "")

    if tipo_documento == "listado":
        tex = _strip_block(tex, "%% BLOCK_MATERIALES_SECTION %%", "%% END_MATERIALES_SECTION %%")
        tex = _strip_block(tex, "%% BLOCK_SERVICIOS_SECTION %%", "%% END_SERVICIOS_SECTION %%")
        tex = _strip_block(tex, "%% BLOCK_DETALLE_TOTALES %%", "%% END_DETALLE_TOTALES %%")
        nombres = [item["nombre"] for item in cart_items] + [s["nombre"] for s in service_items]
        tex = tex.replace(
            "BLOCK_LISTADO_ITEMS",
            "\n".join(f"\\item {_escape_latex(nombre)}" for nombre in nombres),
        )
        if project_header:
            tex = tex.replace("DESCRIPCION_PROYECTO", _escape_latex(project_header))
        else:
            tex = _strip_block(tex, "%% BLOCK_DESCRIPCION %%", "%% END_DESCRIPCION %%")
    elif tipo_documento == "solo_total":
        tex = _strip_block(tex, "%% BLOCK_MATERIALES_SECTION %%", "%% END_MATERIALES_SECTION %%")
        tex = _strip_block(tex, "%% BLOCK_SERVICIOS_SECTION %%", "%% END_SERVICIOS_SECTION %%")
        tex = _strip_block(tex, "%% BLOCK_DETALLE_TOTALES %%", "%% END_DETALLE_TOTALES %%")
        tex = _strip_block(tex, "%% BLOCK_LISTADO_SECTION %%", "%% END_LISTADO_SECTION %%")
        if project_header:
            tex = tex.replace("DESCRIPCION_PROYECTO", _escape_latex(project_header))
        else:
            tex = _strip_block(tex, "%% BLOCK_DESCRIPCION %%", "%% END_DESCRIPCION %%")
    else:
        if cart_items:
            filas = []
            for item in cart_items:
                filas.append(
                    f"{_escape_latex(item['nombre'])} & {item['cantidad']} & "
                    f"{clp(item['precio_unitario'])} & "
                    f"{clp(item['cantidad'] * item['precio_unitario'])} \\\\")
            tex = tex.replace("\nBLOCK_MATERIALES\n", "\n" + "\n".join(filas) + "\n")
        else:
            tex = _strip_block(tex, "%% BLOCK_MATERIALES_SECTION %%", "%% END_MATERIALES_SECTION %%")

        if service_items:
            filas = []
            for service in service_items:
                filas.append(
                    f"{_escape_latex(service['nombre'])} & {clp(service['valor'])} \\\\")
            tex = tex.replace("\nBLOCK_SERVICIOS\n", "\n" + "\n".join(filas) + "\n")
        else:
            tex = _strip_block(tex, "%% BLOCK_SERVICIOS_SECTION %%", "%% END_SERVICIOS_SECTION %%")

        tex = _strip_block(tex, "%% BLOCK_DESCRIPCION %%", "%% END_DESCRIPCION %%")
        tex = _strip_block(tex, "%% BLOCK_LISTADO_SECTION %%", "%% END_LISTADO_SECTION %%")

    if totals["descuento"] > 0:
        tex = tex.replace("DESCUENTO_LABEL", "Descuento")
        tex = tex.replace("TOTAL_DESCUENTO", clp(totals["descuento"]))
    else:
        tex = _strip_block(tex, "%% BLOCK_DESCUENTO_ROW %%", "%% END_DESCUENTO_ROW %%")

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


def generate_pdf(project_title, project_header, cart_items, service_items, totals, tipo_documento="detallado", logo_path="1.png"):
    """Compila la plantilla canonica con pdflatex y devuelve bytes PDF."""
    if shutil.which("pdflatex") is None:
        raise RuntimeError("No se encontro pdflatex en este entorno.")

    tex = build_latex(project_title, project_header, cart_items, service_items, totals, tipo_documento)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        tex_path = tmp_path / "presupuesto.tex"
        tex_path.write_text(tex, encoding="utf-8")

        logo = Path(logo_path) if logo_path else None
        if logo and logo.exists():
            shutil.copy2(logo, tmp_path / logo.name)

        last_output = ""
        for _ in range(2):
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
                cwd=tmpdir,
                capture_output=True,
                check=False,
            )
            last_output = (result.stdout + result.stderr).decode(
                "utf-8", errors="replace"
            )
            if result.returncode == 0 and (tmp_path / "presupuesto.pdf").exists():
                return (tmp_path / "presupuesto.pdf").read_bytes()

    diagnostico = " ".join(last_output.splitlines()[-8:])
    raise RuntimeError(f"pdflatex no pudo generar el PDF. {diagnostico}")
