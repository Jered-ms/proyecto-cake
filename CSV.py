import csv 
from cake import Cake

def torta_csv(nombre_archivo, tortas):
    with open(nombre_archivo, 'w') as archivo:
      escritor = csv.writer(archivo)
      escritor.writerow(['porciones', 'sabor', 'rellenos', 'imagen', 'precio'])
      for torta in tortas:
        escritor.writerow([torta.porciones, torta.sabor,";".join(torta.rellenos), torta.imagen, torta.precio])
        print("Torta guardada en CSV")

tortas = []

torta_de_frambuesa = Cake()
torta_de_frambuesa.agregar_torta(30,"vainilla",['manjar','crema','mermelada','chocolate'],'ruta/imagen.JPG')

torta_de_chocolate = Cake()
torta_de_chocolate.agregar_torta(15,"chocolate",['manjar','crema','chocolate'],'ruta/imagen.JPG') 

tortas.append(torta_de_frambuesa)
tortas.append(torta_de_chocolate)
print(tortas)

torta_csv('tortas.csv', tortas)

def escribir_tortas_csv(nombre_archivo, torta):
    with open(nombre_archivo, 'a') as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow([torta.porciones, torta.sabor,";".join(torta.rellenos), torta.imagen, torta.precio])  
        print("Torta guardada en CSV")
torta_selva_negra = Cake()
torta_selva_negra.agregar_torta(15,"chocolate",['crema','mermelada','chocolate'],'ruta/imagen.JPG')
escribir_tortas_csv('tortas.csv',torta_selva_negra)

