import unittest

from kaze_pdf_core import calculate_totals


class PresupuestoTests(unittest.TestCase):
    def setUp(self):
        self.materiales = [{
            "cantidad": 2,
            "precio_unitario": 1000,
        }]
        self.servicios = [{"valor": 3000}]

    def test_descuento_porcentaje(self):
        totals = calculate_totals(self.materiales, self.servicios, "Porcentaje %", 10)
        self.assertEqual(totals["subtotal"], 5000)
        self.assertEqual(totals["descuento"], 500)
        self.assertEqual(totals["total_final"], 4500)

    def test_descuento_fijo_no_supera_subtotal(self):
        totals = calculate_totals(self.materiales, self.servicios, "Monto fijo $", 9000)
        self.assertEqual(totals["descuento"], 5000)
        self.assertEqual(totals["total_final"], 0)

    def test_sin_descuento(self):
        totals = calculate_totals(self.materiales, self.servicios, "Sin descuento", 0)
        self.assertEqual(totals["descuento"], 0)
        self.assertEqual(totals["total_final"], 5000)
