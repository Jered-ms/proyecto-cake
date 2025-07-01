from tkinter import *
from tkinter import messagebox, filedialog
from tkcalendar import Calendar
import csv
import os

USUARIOS = "credenciales.csv"
PEDIDOS_CSV = "pedidos.csv"
MAX_PEDIDOS_DIARIOS = 100


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

    try:
        with open(USUARIOS, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["correo"] == correo or row["rut"] == rut:
                    messagebox.showwarning("Registro duplicado", "Este usuario ya está registrado.")
                    return
    except FileNotFoundError:
        pass

    archivo_nuevo = not os.path.exists(USUARIOS)
    with open(USUARIOS, "a", newline="") as f:
        writer = csv.writer(f)
        if archivo_nuevo:
            writer.writerow(["nombre", "correo", "rut"])
        writer.writerow([nombre, correo, rut])

    messagebox.showinfo("Registro", "Usuario registrado correctamente.")
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
        messagebox.showerror("Error", "No hay usuario registrado.\nUse primero el botón Registrar")
        return

    if cred and cred["nombre"] == nombre and cred["correo"] == correo and cred["rut"] == rut:
        messagebox.showinfo("Ingreso", "Usuario ingresado correctamente")
        aplication.withdraw()
        mostrar_vista_pedido()
    else:
        messagebox.showerror("Error", "Nombre, Correo o RUT incorrectos")


def pedidos_para_fecha(fecha):
    try:
        with open(PEDIDOS_CSV, newline="") as f:
            reader = csv.DictReader(f)
            return sum(1 for row in reader if row["fecha"] == fecha)
    except FileNotFoundError:
        return 0


def mostrar_vista_pedido():
    ventana_pedido = Toplevel()
    ventana_pedido.geometry("800x600")
    ventana_pedido.title("Formulario de Pedido")
    ventana_pedido.config(bg="LavenderBlush")

    Label(ventana_pedido, text="Cantidad de porciones", bg="LavenderBlush").pack(anchor="w", padx=10, pady=10)
    porciones_var = StringVar(value="Seleccionar")
    opciones_porciones = ["15", "20", "30", "50"]
    OptionMenu(ventana_pedido, porciones_var, *opciones_porciones).pack(fill="x", padx=15)

    Label(ventana_pedido, text="Sabor del bizcocho", bg="LavenderBlush").pack(anchor="w", padx=10, pady=10)
    sabor_var = StringVar(value="Seleccionar")
    opciones_sabor = ["chocolate", "vainilla", "mármol"]
    OptionMenu(ventana_pedido, sabor_var, *opciones_sabor).pack(fill="x", padx=15)

    Label(ventana_pedido, text="Tipo de relleno (selecciona al menos uno)", bg="LavenderBlush").pack(anchor="w", padx=10, pady=10)
    rellenos = {
        "manjar": BooleanVar(),
        "crema pastelera": BooleanVar(),
        "crema chantilly": BooleanVar(),
        "crema de chocolate": BooleanVar(),
        "lúcuma": BooleanVar()
    }
    for relleno, var in rellenos.items():
        Checkbutton(ventana_pedido, text=relleno.capitalize(), variable=var, bg="LavenderBlush").pack(anchor="w", padx=30)

    Label(ventana_pedido, text="Imagen de referencia (JPG)", bg="LavenderBlush").pack(anchor="w", padx=10, pady=10)
    imagen_var = StringVar(value="")

    def seleccionar_imagen():
        ruta = filedialog.askopenfilename(filetypes=[("JPG files", "*.jpg")])
        if ruta:
            imagen_var.set(ruta)

    Button(ventana_pedido, text="Seleccionar imagen", command=seleccionar_imagen).pack(pady=5)

    Label(ventana_pedido, text="Fecha de entrega", bg="LavenderBlush").pack(anchor="w", padx=10, pady=10)
    calendario = Calendar(ventana_pedido, selectmode='day', date_pattern='yyyy-mm-dd')
    calendario.pack(pady=10)

    def enviar_pedido():
        porciones = porciones_var.get()
        sabor = sabor_var.get()
        imagen = imagen_var.get()
        fecha = calendario.get_date()
        rellenos_seleccionados = [r for r, v in rellenos.items() if v.get()]
        cantidad_rellenos = len(rellenos_seleccionados)

        if porciones == "Seleccionar" or sabor == "Seleccionar" or not rellenos_seleccionados:
            messagebox.showwarning("Campos obligatorios", "Debe seleccionar porciones, sabor y al menos un relleno.")
            return
        if not imagen:
            messagebox.showwarning("Imagen faltante", "Debe seleccionar una imagen JPG de referencia.")
            return

        pedidos_existentes = pedidos_para_fecha(fecha)
        if pedidos_existentes >= MAX_PEDIDOS_DIARIOS:
            respuesta = messagebox.askquestion("Sin disponibilidad", f"No hay disponibilidad para la fecha {fecha}. ¿Deseas volver a cotizar?")
            if respuesta == "yes":
                ventana_pedido.destroy()
                aplication.deiconify()
            else:
                ventana_pedido.destroy()
            return

        print(f"Cantidad de rellenos seleccionados: {cantidad_rellenos}")

        archivo_nuevo = not os.path.exists(PEDIDOS_CSV)
        with open(PEDIDOS_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if archivo_nuevo:
                writer.writerow(["porciones", "sabor", "rellenos", "imagen", "fecha"])
            writer.writerow([porciones, sabor, "; ".join(rellenos_seleccionados), imagen, fecha])

        messagebox.showinfo("Pedido", f"¡Pedido enviado correctamente!\nFecha: {fecha}")
        ventana_pedido.destroy()
        aplication.deiconify()

    Button(ventana_pedido, text="Obtener presupuesto", bg="#B0E0E6", command=enviar_pedido).pack(pady=20)

    ventana_pedido.protocol("WM_DELETE_WINDOW", lambda: [ventana_pedido.destroy(), aplication.deiconify()])


# Interfaz principal
aplication = Tk()
aplication.geometry("1500x700+0+0")
aplication.title("Ingreso Pastelería")
aplication.config(bg="AliceBlue")

Label(aplication, text="Nombre", bg="AliceBlue").pack(anchor="w", padx=10, pady=15)
entry_nombre = Entry(aplication)
entry_nombre.pack(fill="x", padx=15)

Label(aplication, text="Correo", bg="AliceBlue").pack(anchor="w", padx=10, pady=15)
entry_correo = Entry(aplication)
entry_correo.pack(fill="x", padx=15)

Label(aplication, text="RUT", bg="AliceBlue").pack(anchor="w", padx=10, pady=15)
entry_rut = Entry(aplication)
entry_rut.pack(fill="x", padx=15)

frame_btns = Frame(aplication, bg="MistyRose1")
frame_btns.pack(pady=30)

btn_registrar = Button(frame_btns, text="Registrar", bg="#DDA0DD", command=registrar_cliente)
btn_registrar.pack(side="left", padx=10)

btn_ingresar = Button(frame_btns, text="Ingresar", bg="#DDA0DD", command=ingresar_cliente)
btn_ingresar.pack(side="left", padx=10)

aplication.mainloop()
