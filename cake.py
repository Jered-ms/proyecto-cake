class Cake:
    def __init__(self):
        self.porciones = 0
        self.sabor = ''
        self.rellenos = []
        self.imagen = ''
        self.precio = 0

    def agregar_torta(self,porciones,sabor,rellenos,imagen):
        precio = 0
        precio_porcion = {
            15:15000,
            20:20000,
            30:25000,
            50:40000
        }
        if len(rellenos) >= 3:
            precio = 2000 * (len(rellenos)-3) + precio_porcion[int(porciones)] 
        else:
            precio = precio_porcion[int(porciones)]

        self.porciones = int(porciones)
        self.sabor = str(sabor.lower())
        self.rellenos = rellenos
        self.imagen = str(imagen)
        self.precio = precio

#torta_de_frambuesa = Cake()
#torta_de_frambuesa.agregar_torta(30,"vainilla",['manjar','crema','mermelada','chocolate'],'ruta/imagen.JPG')
#print(torta_de_frambuesa.precio) 