from tkinter import *
from tkinter import messagebox
import csv
import os
from tkcalendar import Calendar

USUARIOS = "credenciales.csv"



def validar_campos():
    nombre = entry_nombre.get().strip()
    correo = entry_correo.get().strip()
    rut = entry_rut.get().strip()

    if not nombre:
        messagebox.showwarning("Campo obligatorio", "El campo Nombre es obligatorio.")
        return
    if not correo:
        messagebox.showwarning("Campo obligatorio", "El campo Correo es obligatorio.")
        return
    if not rut:
        messagebox.showwarning("Campo obligatorio", "El campo RUT es obligatorio.")
        return

    return correo, rut, nombre


def registrar_cliente():
    try:
        correo, rut, nombre = validar_campos()
    except ValueError:
        return

    # Verificar si el usuario ya existe
    try:
        with open(USUARIOS, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["correo"] == correo or row["rut"] == rut:
                    messagebox.showwarning("Registro duplicado", "Este usuario ya está registrado.")
                    return
    except FileNotFoundError:
        # Archivo no existe aún, se creará más abajo
        pass

    # Registrar usuario nuevo
    archivo_nuevo = not os.path.exists(USUARIOS)
    with open(USUARIOS, "a", newline="") as f:
        writer = csv.writer(f)
        if archivo_nuevo:
            writer.writerow(["nombre", "correo", "rut"])
        writer.writerow([nombre, correo, rut])

    messagebox.showinfo("Registro", "Usuario registrado correctamente.")

    # Limpiar campos
    entry_nombre.delete(0, END)
    entry_correo.delete(0, END)
    entry_rut.delete(0, END)


def ingresar_cliente():
    try:
        correo, rut, nombre = validar_campos()
    except ValueError:
        return
    try:
        with open(USUARIOS, newline="") as f:
            reader = csv.DictReader(f)
            cred = next(reader, None)
    except FileNotFoundError:
        messagebox.showerror("Error" , "No hay usuario registrado.\nUse primero el botón Registrar")
        return
  
    if cred and cred["nombre"] == nombre and cred["correo"] == correo and cred["rut"] == rut:
      messagebox.showinfo("ingreso", "Usuario ingresado correctamente")
      aplication.withdraw()
      mostrar_vista_pedido()
    else:
      messagebox.showerror("error", "Nombre, Correo o rut incorrectos")




"----------------------------------------------------------------------------"    

def mostrar_vista_pedido():
    ventana_pedido = Toplevel()
    ventana_pedido.geometry("800x600")
    ventana_pedido.title("Formulario de Pedido")
    ventana_pedido.config(bg="LavenderBlush")

    Label(ventana_pedido, text="Dirección de entrega", bg="LavenderBlush").pack(anchor="w", padx=10, pady=10)
    entry_direccion = Entry(ventana_pedido)
    entry_direccion.pack(fill="x", padx=15)

    Label(ventana_pedido, text="Producto", bg="LavenderBlush").pack(anchor="w", padx=10, pady=10)
    entry_producto = Entry(ventana_pedido)
    entry_producto.pack(fill="x", padx=15)

    Label(ventana_pedido, text="Cantidad", bg="LavenderBlush").pack(anchor="w", padx=10, pady=10)
    entry_cantidad = Entry(ventana_pedido)
    entry_cantidad.pack(fill="x", padx=15)

    # Calendario para seleccionar la fecha
    Label(ventana_pedido, text="Fecha de entrega", bg="LavenderBlush").pack(anchor="w", padx=10, pady=10)
    calendario = Calendar(ventana_pedido, selectmode='day', date_pattern='yyyy-mm-dd')
    calendario.pack(pady=10)

    def enviar_pedido():
        direccion = entry_direccion.get()
        producto = entry_producto.get()
        cantidad = entry_cantidad.get()
        fecha = calendario.get_date()

        if not direccion or not producto or not cantidad:
            messagebox.showwarning("Campos obligatorios", "Todos los campos deben ser completados.")
            return

        messagebox.showinfo("Pedido", f"¡Pedido enviado correctamente!\nFecha: {fecha}")
        ventana_pedido.destroy()
        aplication.deiconify()

    Button(ventana_pedido, text="Enviar Pedido", bg="#B0E0E6", command=enviar_pedido).pack(pady=20)

    ventana_pedido.protocol("WM_DELETE_WINDOW", lambda: [ventana_pedido.destroy(), aplication.deiconify()])


"----------------------------------------------------------------------------"    
    
aplication = Tk()
aplication.geometry("1500x700+0+0")
aplication.title("Ingreso Pasteleria")
aplication.config(bg="AliceBlue")

#CAMPO NOMBRE
Label(aplication, text="Nombre", bg="AliceBlue").pack(anchor="w", padx=10, pady=15)
entry_nombre=Entry(aplication)
entry_nombre.pack(fill="x", padx=15)

#CAMPO CORREO
Label(aplication, text="Correo", bg="AliceBlue").pack(anchor="w", padx=10, pady=15)
entry_correo=Entry(aplication)
entry_correo.pack(fill="x", padx=15)

#CAMPO RUT
Label(aplication, text="Rut", bg="AliceBlue").pack(anchor="w", padx=10, pady=15)
entry_rut=Entry(aplication)
entry_rut.pack(fill="x", padx=15)

frame_btns = Frame(aplication, bg="MistyRose1")
frame_btns.pack(pady=30)

btn_registrar = Button(frame_btns, text="Registrar", bg="#DDA0DD", command= registrar_cliente)
btn_registrar.pack(side="left" , padx=10)

btn_ingresar = Button(frame_btns, text="Ingresar", bg="#DDA0DD", command= ingresar_cliente)
btn_ingresar.pack(side="left" , padx=10)


aplication.mainloop()

