from tkinter import *
from tkinter import messagebox, filedialog
from tkcalendar import Calendar
import csv
import os
import random
import re

from user import Admin
from user import User
from cake import Cake
from order import Order
from datetime import datetime
from stock import Stock

USUARIOS = "credenciales.csv"
PEDIDOS_CSV = "pedidos.csv"
MAX_PEDIDOS_DIARIOS = 100

def correo_valido(correo):
    return re.match(r"^[\w\.-]+@gmail\.com$", correo)

def rut_valido(rut):
    return re.match(r"^\d{7,8}-[\dkK]$", rut)

def normalizar(nombre):
    return nombre.strip().upper().replace(" ", "_")

def validar_campos(entry_nombre,entry_correo,entry_rut):
    nombre = entry_nombre.get().strip()
    correo = entry_correo.get().strip()
    rut = entry_rut.get().strip()

    if not correo_valido(correo):
        messagebox.showwarning("Correo inválido", "El correo debe ser de formato válido y de preferencia @gmail.com.")
        return
    if not rut_valido(rut):
        messagebox.showwarning("RUT inválido", "Debe ingresar un RUT válido con guión (ej: 12345678-9).")
        return
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


def pedidos_para_fecha(fecha):
    try:
        with open(PEDIDOS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if "fecha" not in reader.fieldnames:
                raise ValueError("Falta la columna 'fecha'")

            return sum(1 for row in reader if validar_fecha(row.get("fecha")) and row["fecha"] == fecha)
    except FileNotFoundError:
        return 0
    except Exception as e:
        messagebox.showerror("Error", f"Error leyendo pedidos:\n{e}")
        return 0

def validar_fecha(fecha_str):
    try:
        datetime.strptime(fecha_str, "%Y-%m-%d")
        return True
    except:
        return False

def registrar_cliente(entry_nombre, entry_correo, entry_rut):

    try:
        correo, rut, nombre = validar_campos(entry_nombre, entry_correo, entry_rut)
        user = User(nombre, rut, correo, "cliente")
    except ValueError:
        return

    try:
        with open(USUARIOS, "r", newline="",encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != ["nombre", "correo", "rut"]:
                messagebox.showerror("Error", "El archivo de usuarios tiene un formato incorrecto.")
                return
            for row in reader:
                if row["correo"] == correo or row["rut"] == rut:
                    messagebox.showwarning("Registro duplicado", "Este usuario ya está registrado.")
                    return
    except FileNotFoundError:
        pass

    archivo_nuevo = not os.path.exists(USUARIOS)
    with open(USUARIOS, "a", newline="",encoding="utf-8") as f:
        writer = csv.writer(f)
        if archivo_nuevo:
            writer.writerow(["nombre", "correo", "rut"])
        writer.writerow([user.nombre, user.correo, user.rut])

    messagebox.showinfo("Registro", "Usuario registrado correctamente.")
    entry_nombre.delete(0, END)
    entry_correo.delete(0, END)
    entry_rut.delete(0, END)


def ingresar_cliente(inventario, aplication,entry_nombre,entry_correo,entry_rut):
    try:
        correo, rut, nombre = validar_campos(entry_nombre,entry_correo,entry_rut)
    except ValueError:
        return

    user_input = User(nombre, rut, correo, "cliente")

    try:
        with open(USUARIOS, newline="",encoding="utf-8") as f:
            reader = csv.DictReader(f)
            filas = list(reader)  
    except FileNotFoundError:
        messagebox.showerror("Error", "No hay usuario registrado.\nUse primero el botón Registrar")
        return

    match = any(row["nombre"].lower() == user_input.nombre and 
                row["correo"] == user_input.correo and 
                row["rut"] == user_input.rut for row in filas)

    if match:
        messagebox.showinfo("Ingreso", "Usuario ingresado correctamente")
        aplication.withdraw()
        mostrar_vista_pedido(user_input, inventario, aplication)
    else:
        messagebox.showerror("Error", "Nombre, Correo o RUT incorrectos")


def mostrar_vista_admin(ventana_admin, inventario):
    for widget in ventana_admin.winfo_children():
        widget.destroy()

    ventana_admin.title("Panel del Administrador")

    Label(ventana_admin, text="Panel de administración", font=("Arial", 16, "bold"), bg="LavenderBlush").pack(pady=20)


    def modificar_stock(ventana_admin, stock_obj):
        # Limpia lo que haya actualmente en la ventana
        for widget in ventana_admin.winfo_children():
            widget.destroy()

        Label(ventana_admin, text="Modificar Stock de Ingredientes", font=("Arial", 16, "bold"), bg="LavenderBlush").pack(pady=20)

        entradas_stock = {}  # diccionario para guardar los campos de entrada por ingrediente

        for ingrediente in stock_obj.inventario:
            frame = Frame(ventana_admin, bg="LavenderBlush")
            frame.pack(pady=5)

            Label(frame, text=ingrediente.replace("_", " ").title(), width=20, anchor="w", bg="LavenderBlush").pack(side="left", padx=5)
            entrada = Entry(frame, width=10)
            entrada.insert(0, str(stock_obj.inventario[ingrediente]))
            entrada.pack(side="left")
            entradas_stock[ingrediente] = entrada

        def guardar_stock():
            for ingrediente, entrada in entradas_stock.items():
                nuevo_valor = entrada.get()
                if not nuevo_valor.isdigit():
                    messagebox.showerror("Error", f"El valor para {ingrediente} debe ser un número entero.")
                    return
                stock_obj.modificar_inventario(ingrediente, int(nuevo_valor))

            messagebox.showinfo("Éxito", "Stock actualizado correctamente.")
            mostrar_vista_admin(ventana_admin,inventario)

        Button(ventana_admin, text="Guardar cambios", bg="#90EE90", command=guardar_stock).pack(pady=20)
        Button(ventana_admin, text="Volver al menú", bg="#B0E0E6", command=lambda: mostrar_vista_admin(ventana_admin,inventario)).pack(pady=5)


    def ver_pedidos():
        if not os.path.exists(PEDIDOS_CSV):
            messagebox.showinfo("Pedidos", "Aún no hay pedidos registrados.")
            return

        with open(PEDIDOS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            pedidos = list(reader)

        texto = "\n\n".join([
            f"ID: {p['ID']}\nCliente: {p['usuario']}\nCorreo: {p['correo']}\nRUT: {p['rut']}\nFecha: {p['fecha']}\nPrecio: ${p['precio']}"
            for p in pedidos
        ])

        messagebox.showinfo("Listado de pedidos", texto if texto else "No hay pedidos registrados.")

    def ver_fechas_entrega():
        if not os.path.exists(PEDIDOS_CSV):
            messagebox.showinfo("Fechas", "No hay fechas registradas aún.")
            return

        with open(PEDIDOS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fechas = sorted(set(row["fecha"] for row in reader if "fecha" in row))

        texto = "\n".join(fechas)
        messagebox.showinfo("Fechas de entrega agendadas", texto if texto else "No hay fechas registradas.")

    Button(ventana_admin, text="Modificar stock", bg="#DDA0DD", width=25, command=lambda:modificar_stock(ventana_admin,inventario)).pack(pady=10)
    Button(ventana_admin, text="Ver listado de pedidos", bg="#DDA0DD", width=25, command=ver_pedidos).pack(pady=10)
    Button(ventana_admin, text="Ver fechas de entrega", bg="#DDA0DD", width=25, command=ver_fechas_entrega).pack(pady=10)

    Button(ventana_admin, text="Cerrar sesión", bg="#B0E0E6", command=ventana_admin.destroy).pack(pady=20)


def ingresar_admin(inventario):
    ventana_admin = Toplevel()
    ventana_admin.geometry("400x300")
    ventana_admin.title("Ingreso Administrador")
    ventana_admin.config(bg="LavenderBlush")

    Label(ventana_admin, text="RUT del administrador:", bg="LavenderBlush").pack(pady=10)
    entry_rut_admin = Entry(ventana_admin)
    entry_rut_admin.pack()

    Label(ventana_admin, text="Clave:", bg="LavenderBlush").pack(pady=10)
    entry_clave_admin = Entry(ventana_admin, show="*")
    entry_clave_admin.pack()

    def validar_admin(inventario):
        rut_ingresado = entry_rut_admin.get().strip()
        if not rut_valido(rut_ingresado):
            messagebox.showwarning("RUT inválido", "Debe ingresar un RUT válido con guión (ej: 12345678-9).")
        clave_ingresada = entry_clave_admin.get().strip()

        admin = Admin()
        if rut_ingresado == admin.rut and clave_ingresada == admin.clave:
            #messagebox.showinfo("Ingreso exitoso", "Bienvenido, administrador.")
            mostrar_vista_admin(ventana_admin, inventario)
        else:
            messagebox.showerror("Error", "RUT o clave incorrecta.")

    def volver_atras():
        ventana_admin.destroy()

    Button(ventana_admin, text="Ingresar", bg="#DDA0DD", command=lambda:validar_admin(inventario)).pack(pady=10)
    Button(ventana_admin, text="Volver atrás", bg="#B0E0E6", command=volver_atras).pack(pady=10)


def mostrar_sin_disponibilidad(fecha, ventana_pedido, aplication):
    ventana_no_disponible = Toplevel()
    ventana_no_disponible.geometry("400x200")
    ventana_no_disponible.title("Sin disponibilidad")
    ventana_no_disponible.config(bg="LavenderBlush")
    
    Label(ventana_no_disponible, text=f"No hay disponibilidad para la fecha {fecha}", 
          bg="LavenderBlush", wraplength=350).pack(pady=20)
    
    frame_btns = Frame(ventana_no_disponible, bg="LavenderBlush")
    frame_btns.pack(pady=20)
    
    def volver_cotizar():
        ventana_no_disponible.destroy()
    
    def salir():
        ventana_no_disponible.destroy()
        ventana_pedido.destroy()
        aplication.quit()
    
    Button(frame_btns, text="Volver a cotizar", command=volver_cotizar).pack(side="left", padx=10)
    Button(frame_btns, text="Salir", command=salir).pack(side="left", padx=10)

def mostrar_presupuesto(torta, pedido, user, fecha, ventana_pedido, aplication,inventario):
    ventana_presupuesto = Toplevel()
    ventana_presupuesto.geometry("500x400")
    ventana_presupuesto.title("Presupuesto")
    ventana_presupuesto.config(bg="LavenderBlush")
    
    Label(ventana_presupuesto, text="DETALLE DEL PRESUPUESTO", 
          font=("Arial", 16, "bold"), bg="LavenderBlush").pack(pady=10)
    
    detalles = f"""
        Cliente: {user.nombre}
        Porciones: {torta.porciones}
        Sabor: {torta.sabor}
        Rellenos: {', '.join(torta.rellenos)}
        Fecha de entrega: {fecha}
        PRECIO TOTAL: ${torta.precio:,}
    """
    
    Label(ventana_presupuesto, text=detalles, bg="LavenderBlush", 
          justify="left", font=("Arial", 12)).pack(pady=20)
    
    frame_btns = Frame(ventana_presupuesto, bg="LavenderBlush")
    frame_btns.pack(pady=20)
    
    def encargar(inventario):

        for ing in torta.rellenos:
          inventario.restar_stock(ing, 1)      

        archivo_nuevo = not os.path.exists(PEDIDOS_CSV)
        with open(PEDIDOS_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if archivo_nuevo:
                writer.writerow(["ID", "usuario", "correo", "rut", "porciones", "sabor", "rellenos", "imagen", "fecha", "precio"])
            writer.writerow([
                pedido.ID,
                user.nombre,
                user.correo,
                user.rut,
                torta.porciones,
                torta.sabor,
                "; ".join(torta.rellenos),
                torta.imagen,
                fecha,
                torta.precio
            ])

        
        ventana_presupuesto.destroy()
        mostrar_info_retiro(fecha, ventana_pedido, aplication)
    
    def salir():
        ventana_presupuesto.destroy()
        ventana_pedido.destroy()
        aplication.quit()
    
    Button(frame_btns, text="Encargar", bg="#90EE90", command=lambda: encargar(inventario)).pack(side="left", padx=10)
    Button(frame_btns, text="Salir", command=salir).pack(side="left", padx=10)

def mostrar_info_retiro(fecha, ventana_pedido, aplication):
    ventana_retiro = Toplevel()
    ventana_retiro.geometry("400x300")
    ventana_retiro.title("Información de retiro")
    ventana_retiro.config(bg="LavenderBlush")
    
    Label(ventana_retiro, text="¡PEDIDO CONFIRMADO!", 
          font=("Arial", 16, "bold"), bg="LavenderBlush").pack(pady=20)
    
    info_retiro = f"""
        Dirección de la pastelería:
        Av. Providencia 1234
        Las Condes, Santiago

        Fecha de retiro: {fecha}
        Horario de atención: 9:00 - 18:00 hrs

        ¡Gracias por su preferencia!
    """
    
    Label(ventana_retiro, text=info_retiro, bg="LavenderBlush", 
          justify="center", font=("Arial", 12)).pack(pady=20)
    
    def cerrar():
        ventana_retiro.destroy()
        ventana_pedido.destroy()
        aplication.deiconify()
    
    Button(ventana_retiro, text="Cerrar", bg="#B0E0E6", command=cerrar).pack(pady=20)


def mostrar_vista_pedido(user, inventario, aplication):
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

    def enviar_pedido(inventario, aplication):
        porciones = porciones_var.get()
        sabor = sabor_var.get()
        imagen = imagen_var.get()
        fecha = calendario.get_date()
        rellenos_seleccionados = [r for r, v in rellenos.items() if v.get()]
    
        if porciones == "Seleccionar" or sabor == "Seleccionar" or not rellenos_seleccionados:
            messagebox.showwarning("Campos obligatorios", "Debe seleccionar porciones, sabor y al menos un relleno.")
            return
        if not imagen:
            messagebox.showwarning("Imagen faltante", "Debe seleccionar una imagen JPG de referencia.")
            return

        pedidos_existentes = pedidos_para_fecha(fecha)
        if pedidos_existentes >= MAX_PEDIDOS_DIARIOS:
            mostrar_sin_disponibilidad(fecha, ventana_pedido, aplication)
            return

        torta = Cake()
        torta.agregar_torta(porciones, sabor, rellenos_seleccionados, imagen)

        pedido = Order()
        id = random.randint(1, 1000000)
        pedido.agregar_order(id, cake=torta)

        mostrar_presupuesto(torta, pedido, user, fecha, ventana_pedido, aplication,inventario)

    Button(ventana_pedido, text="Obtener presupuesto", bg="#B0E0E6", command=lambda: enviar_pedido(inventario,aplication)).pack(pady=20)

    ventana_pedido.protocol("WM_DELETE_WINDOW", lambda: [ventana_pedido.destroy(), aplication.deiconify()])

def main():
    inventario = Stock()
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

    btn_registrar = Button(frame_btns, text="Registrar", bg="#DDA0DD", command=lambda: registrar_cliente(entry_nombre, entry_correo, entry_rut))
    btn_registrar.pack(side="left", padx=10)

    btn_admin = Button(frame_btns, text="Ingresar Admin", bg="#DDA0DD", command=lambda: ingresar_admin(inventario))
    btn_admin.pack(side="left", padx=10)

    btn_ingresar = Button(frame_btns, text="Ingresar", bg="#DDA0DD", command=lambda: ingresar_cliente(inventario, aplication,entry_nombre,entry_correo,entry_rut))
    btn_ingresar.pack(side="left", padx=10)

    aplication.mainloop()

if __name__ == "__main__":
    main()