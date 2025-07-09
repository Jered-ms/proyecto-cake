class Stock:
    def __init__(self):
        self.inventario = {
            'MANJAR': 10,
            'CREMA_PASTELERA': 10,
            'CREMA_CHANTILLY': 10,
            'CREMA_DE_CHOCOLATE': 10,
            'LUCUMA': 10
        }

    def modificar_inventario(self, ingrediente, cantidad):
        self.inventario[ingrediente] = int(cantidad)

    def restar_stock(self, ingrediente, cantidad):
        if ingrediente not in self.inventario:
            print(f"Ingrediente '{ingrediente}' no encontrado en el inventario.")
            return
        if self.inventario[ingrediente] < int(cantidad):
            print(f"No hay suficiente stock de {ingrediente}. Stock disponible: {self.inventario[ingrediente]}")
            return
        self.inventario[ingrediente] -= int(cantidad)

    