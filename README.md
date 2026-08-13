# KAZE PDF CORE

Motor compartido de presupuestos KaZe.

Version estable actual: `v0.1.2`.

Repositorio publico: https://github.com/jjaavviieer123-rgb/KAZE-PDF-CORE

## Fuente de formato

`src/kaze_pdf_core/plantilla.tex` deriva de la plantilla que utilizaba la
aplicación Streamlit. Esa plantilla es la fuente canónica del formato PDF.
Los marcadores `%% ... %%` son comentarios de control y no cambian el diseño.

## Uso

El motor no depende de Streamlit, Telegram ni Google Sheets. Recibe los datos
del presupuesto, calcula los totales y compila la plantilla con `pdflatex`.
Si existe `1.png` en el directorio de ejecución, también lo incorpora al
encabezado como hacía la aplicación Streamlit original.

El entorno debe instalar los paquetes LaTeX indicados por cada aplicación,
incluyendo las fuentes usadas por la plantilla.
ReportLab no forma parte del camino compartido porque produciría un formato
distinto.

## Desarrollo

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Versionado

Las aplicaciones deben fijar una etiqueta o commit concreto de este repositorio
para que una actualización del formato sea deliberada y reversible.

La version `v0.1.2` conserva el logo, incluye las fuentes requeridas por la
plantilla y devuelve el diagnostico resumido de `pdflatex` cuando la compilacion
falla.
