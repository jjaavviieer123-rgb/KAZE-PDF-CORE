"""Calculos y validaciones puros del presupuesto."""


def validar_descuento(tipo, valor, subtotal):
    if tipo == "Porcentaje %" and (valor is None or valor < 0 or valor > 100):
        return "El porcentaje de descuento debe estar entre 0 y 100."
    if tipo == "Monto fijo $" and (valor is None or valor < 0):
        return "El monto de descuento debe ser mayor o igual a 0."
    return None


def calculate_discount(subtotal, discount_type, discount_value):
    if not discount_value:
        return 0.0
    if discount_type == "Porcentaje %":
        descuento = subtotal * (discount_value / 100)
    elif discount_type == "Monto fijo $":
        descuento = discount_value
    else:
        descuento = 0.0
    return max(0.0, min(descuento, subtotal))


def calculate_totals(cart_items, service_items, discount_type, discount_value):
    total_materiales = sum(i["cantidad"] * i["precio_unitario"] for i in cart_items)
    total_servicios = sum(i["valor"] for i in service_items)
    subtotal = total_materiales + total_servicios
    descuento = calculate_discount(subtotal, discount_type, discount_value)
    total_final = subtotal - descuento
    return {
        "total_materiales": total_materiales,
        "total_servicios": total_servicios,
        "subtotal": subtotal,
        "descuento": descuento,
        "total_final": total_final,
    }
