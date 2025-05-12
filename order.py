from cake import Cake

class Order:
    def __init__(self):
        self.ID = 0
        self.cake = None
        self.creado = False

    def agregar_order(self,ID,cake):
        self.ID = int(ID)
        self.cake = cake
        self.creado = True

    def mostrar_order(self):
        if self.creado == True:
            print("Pedido creado exitosamente")
            print(f"ID del pedido: {self.ID}")
            print(f"{self.cake}")

torta_de_frambuesa = Cake()
torta_de_frambuesa.agregar_torta(30,"vainilla",['manjar','crema','mermelada','chocolate'],'ruta/imagen.JPG')


pedido = Order()
pedido.agregar_order(1,torta_de_frambuesa)

pedido.mostrar_order()
