import unittest

from kaze_pdf_core import build_latex, calculate_totals, generate_pdf


class PdfTests(unittest.TestCase):
    def setUp(self):
        self.materiales = [{
            "nombre": "Cable THHN",
            "cantidad": 10,
            "precio_unitario": 500,
        }]
        self.servicios = [{"nombre": "Instalación", "valor": 10000}]

    def test_sin_descuento_no_deja_placeholders(self):
        totals = calculate_totals(self.materiales, self.servicios, "Sin descuento", 0)
        tex = build_latex("Obra de prueba", "", self.materiales, self.servicios, totals)
        self.assertNotIn("DESCUENTO_LABEL", tex)
        self.assertNotIn("TOTAL_DESCUENTO", tex)

    def test_con_descuento_muestra_fila(self):
        totals = calculate_totals(self.materiales, self.servicios, "Porcentaje %", 10)
        tex = build_latex("Obra de prueba", "", self.materiales, self.servicios, totals)
        self.assertIn("Descuento:", tex)
        self.assertIn("1.500", tex)

    def test_generates_latex_pdf(self):
        totals = calculate_totals(self.materiales, self.servicios, "Sin descuento", 0)
        pdf = generate_pdf("Obra de prueba", "", self.materiales, self.servicios, totals)
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertGreater(len(pdf), 1000)


if __name__ == "__main__":
    unittest.main()
