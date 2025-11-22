import tkinter as tk
from tkinter import ttk, messagebox 
import time
from bdd import BaseDatos  
from inventario import Inventario 
from producto import Producto  
from venta import Venta  
from ventas import Ventas

class InterfazInventario:
    def __init__(self, root):
        # Inicialización de la clase BaseDatos para manejar la base de datos
        self.base_datos = BaseDatos()
        # Inicialización de la clase Inventario para manejar el inventario de productos
        self.inventario = Inventario()
        # Crea una lista de Ventas
        self.ventas = Ventas()
        # Carga de los productos desde la base de datos al inventario
        self.cargar_productos_desde_db()
        
        # Usuario y rol actuales (se setean en el login)
        self.username = None
        self.user_role = None  # 'Admin' o 'Usuario'
        
        # Configuración de la ventana principal de la aplicación
        self.root = root
        self.root.title("Sistema de Gestión de Inventarios")
        self.root.geometry("800x450")

        # Configuración del notebook para mostrar pestañas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        # Crear barra de menú y barra de herramientas
        self.crear_menu()
        self.crear_toolbar()

        # Creación de las pestañas "Agregar Producto" , "Modificar Producto" , etc
        self.pagina_agregar = ttk.Frame(self.notebook)
        self.pagina_modificar = ttk.Frame(self.notebook)
        self.pagina_estadisticas = ttk.Frame(self.notebook)
        self.pagina_ventas = ttk.Frame(self.notebook)
        self.notebook.add(self.pagina_agregar, text='Agregar Producto')
        self.notebook.add(self.pagina_modificar, text='Modificar Producto')
        self.notebook.add(self.pagina_estadisticas, text='Estadisticas')
        self.notebook.add(self.pagina_ventas, text='Ventas')

        # Creación de la interfaz para agregar un nuevo producto
        self.crear_interfaz_agregar_producto()
        # Creación de la interfaz para modificar un producto existente
        self.crear_interfaz_modificar_producto()
        # Creación del botón para eliminar un producto
        self.crear_boton_eliminar_producto()  # Llamar a la función aquí
        # Creación del botón para mostrar el informe de inventarios
        self.crear_boton_mostrar_informe()
        # Creación de la interfaz de estadísticas
        self.crear_interfaz_estadisticas()
        #Creación de la interfaz para cargar nueva venta
        self.crear_interfaz_agregar_venta()
        #Creación del botón para mostrar ventas
        self.crear_boton_mostrar_ventas()

        # Mostrar ventana de login al iniciar (modal)
        self.mostrar_ventana_login()
        # Aplicar permisos según rol obtenido en el login
        self.aplicar_permisos_por_rol()

    def cargar_productos_desde_db(self):
        productos_db = self.base_datos.obtener_productos()
        self.inventario.productos = productos_db

    def crear_interfaz_agregar_producto(self):
        etiquetas_agregar = ["Nombre del Producto", "Descripción", "Precio", "Stock", "Proveedor"]
        self.entries_agregar = {}
        for i, etiqueta in enumerate(etiquetas_agregar):
            tk.Label(self.pagina_agregar, text=etiqueta, font=("Arial", 12)).grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(self.pagina_agregar, font=("Arial", 12))
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries_agregar[etiqueta] = entry
        self.boton_agregar = tk.Button(self.pagina_agregar, text="Agregar Producto", command=self.agregar_producto, font=("Arial", 12), bg="#4CAF50", fg="white")
        self.boton_agregar.grid(row=len(etiquetas_agregar) + 1, column=0, columnspan=2, pady=10)

    def crear_interfaz_modificar_producto(self):
        etiquetas_modificar = ["Seleccione Producto:", "Nombre del Producto", "Descripción", "Precio", "Stock", "Proveedor"]
        self.combo_modificar = ttk.Combobox(self.pagina_modificar, values=["Seleccionar"] + [producto.nombre for producto in self.inventario.productos], font=("Arial", 12))
        self.combo_modificar.grid(row=0, column=1, padx=10, pady=5)
        self.combo_modificar.set("Seleccionar")
        self.combo_modificar.bind("<<ComboboxSelected>>", self.actualizar_datos_producto_seleccionado)
        self.entries_modificar = {}
        for i, etiqueta in enumerate(etiquetas_modificar[1:]):
            tk.Label(self.pagina_modificar, text=etiqueta, font=("Arial", 12)).grid(row=i + 1, column=0, padx=10, pady=5)
            entry = tk.Entry(self.pagina_modificar, font=("Arial", 12))
            entry.grid(row=i + 1, column=1, padx=10, pady=5)
            self.entries_modificar[etiqueta] = entry
        self.boton_modificar = tk.Button(self.pagina_modificar, text="Modificar Producto", command=self.modificar_producto, font=("Arial", 12), bg="#008CBA", fg="white")
        self.boton_modificar.grid(row=len(etiquetas_modificar) + 1, column=0, columnspan=2, pady=10)

    def crear_boton_eliminar_producto(self):
        # Crea el botón de eliminar en la pestaña de modificación y guarda la referencia
        self.boton_eliminar = tk.Button(self.pagina_modificar,
                                       text="Eliminar Producto",
                                       command=self.eliminar_producto,
                                       font=("Arial", 12),
                                       bg="#FF5733",
                                       fg="white")
        # Ajusta la fila para que no choque con los demás controles
        try:
            row_index = 8
            self.boton_eliminar.grid(row=row_index, column=0, columnspan=2, pady=10)
        except Exception:
            # Si la grilla falla por índices, empaqueta al final como fallback
            self.boton_eliminar.pack(pady=10)

    def crear_interfaz_estadisticas(self):
        total_productos_distintos = len(self.inventario.productos)
        total_productos = sum(producto.cantidad_stock for producto in self.inventario.productos)
        valor_total_inventario = sum(producto.precio * producto.cantidad_stock for producto in self.inventario.productos)
        precio_promedio = valor_total_inventario / total_productos if total_productos > 0 else 0
        
        # Crear etiquetas para mostrar las estadísticas
        etiquetas_estadisticas = [
            f"Cantidad productos distintos: {total_productos_distintos}",
            f"Cantidad Total de Productos: {total_productos}",
            f"Valor Total del Inventario: ${valor_total_inventario:.2f}",
            f"Precio Promedio de Productos: ${precio_promedio:.2f}"
        ]

        # Colocar las etiquetas en la página de estadísticas
        for i, etiqueta in enumerate(etiquetas_estadisticas):
            tk.Label(self.pagina_estadisticas, text=etiqueta, font=("Arial", 12)).grid(row=i, column=0, padx=10, pady=5, sticky='nsew')
        
        # Programar la próxima actualización de las estadísticas en 1 segundo
        self.root.after(1000, self.crear_interfaz_estadisticas)

    def crear_menu(self):
        menubar = tk.Menu(self.root)

        archivo_menu = tk.Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Cerrar sesión", command=self.cerrar_sesion)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)

        inventario_menu = tk.Menu(menubar, tearoff=0)
        inventario_menu.add_command(label="Ir a: Agregar Producto", command=lambda: self.notebook.select(self.pagina_agregar))
        inventario_menu.add_command(label="Ir a: Modificar Producto", command=lambda: self.notebook.select(self.pagina_modificar))
        inventario_menu.add_command(label="Eliminar Producto", command=self.eliminar_producto)
        menubar.add_cascade(label="Inventario", menu=inventario_menu)

        ventas_menu = tk.Menu(menubar, tearoff=0)
        ventas_menu.add_command(label="Mostrar Ventas", command=self.mostrar_ventas)
        menubar.add_cascade(label="Ventas", menu=ventas_menu)

        ayuda_menu = tk.Menu(menubar, tearoff=0)
        ayuda_menu.add_command(label="Acerca de", command=self.mostrar_acerca_de)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)

        self.root.config(menu=menubar)
        # Guardar referencias por si se necesitan
        self._inventario_menu = inventario_menu
        self._archivo_menu = archivo_menu

    def crear_toolbar(self):
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        btn_agregar = tk.Button(toolbar, text="Agregar", command=lambda: self.notebook.select(self.pagina_agregar))
        btn_reporte = tk.Button(toolbar, text="Informe", command=self.mostrar_informe)
        btn_ventas = tk.Button(toolbar, text="Ventas", command=lambda: self.notebook.select(self.pagina_ventas))
        btn_ayuda = tk.Button(toolbar, text="Ayuda", command=self.mostrar_acerca_de)
        btn_agregar.pack(side=tk.LEFT, padx=2, pady=2)
        btn_reporte.pack(side=tk.LEFT, padx=2, pady=2)
        btn_ventas.pack(side=tk.LEFT, padx=2, pady=2)
        btn_ayuda.pack(side=tk.LEFT, padx=2, pady=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

    def crear_interfaz_agregar_venta(self):
        etiquetas_agregar = ["Cantidad Artículos", "Medio de Pago", "Total", "Productos"]
        self.entries_agregar_ventas = {}
        for i, etiqueta in enumerate(etiquetas_agregar):
            tk.Label(self.pagina_ventas, text=etiqueta, font=("Arial", 12)).grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(self.pagina_ventas, font=("Arial", 12))
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries_agregar_ventas[etiqueta] = entry
        self.boton_agregar = tk.Button(self.pagina_ventas, text="Agregar Venta", command=self.agregar_venta, font=("Arial", 12), bg="#4CAF50", fg="white")
        self.boton_agregar.grid(row=len(etiquetas_agregar) + 1, column=0, columnspan=2, pady=10)
    
    def crear_boton_mostrar_ventas(self):
        self.boton_mostrar_informe = tk.Button(self.root, text="Mostrar Ventas", command=self.mostrar_ventas, font=("Arial", 12), bg="#333", fg="white")
        self.boton_mostrar_informe.pack(pady=10)
    

    
    def agregar_venta(self):
        try:
            cant_art = self.entries_agregar_ventas["Cantidad Artículos"].get()
            medio_pago = self.entries_agregar_ventas["Medio de Pago"].get()
            total = float(self.entries_agregar_ventas["Total"].get())
            prodcutos = int(self.entries_agregar_ventas["Productos"].get())
            venta = Venta(len(self.ventas.ventas) + 1, cant_art, medio_pago, total, prodcutos)
            self.ventas.agregar_venta(venta)
            messagebox.showinfo("Éxito", "Producto agregado correctamente.")
        except ValueError:
            messagebox.showerror("Error", "Ingrese datos válidos para el producto.")

    def mostrar_ventas(self):
        informe = self.ventas.generar_informe_ventas()
        mensaje = "\n\n".join(informe)

        # Crear una ventana secundaria para mostrar el informe
        ventana_informe = tk.Toplevel(self.root)
        ventana_informe.title("Informe de Ventas")
        
        # Crear un frame para contener el mensaje con desplazamiento
        frame_mensaje = tk.Frame(ventana_informe)
        frame_mensaje.pack(fill="both", expand=True)

        # Crear un scrollbar para desplazarse verticalmente
        scrollbar = ttk.Scrollbar(frame_mensaje, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        # Crear un Text widget para mostrar el mensaje
        txt_informe = tk.Text(frame_mensaje, yscrollcommand=scrollbar.set)
        txt_informe.pack(fill="both", expand=True)
        txt_informe.insert("1.0", mensaje)

        # Configurar el scrollbar para controlar el desplazamiento del Text widget
        scrollbar.config(command=txt_informe.yview)

    def agregar_producto(self):
        try:
            nombre = self.entries_agregar["Nombre del Producto"].get()
            descripcion = self.entries_agregar["Descripción"].get()
            precio = float(self.entries_agregar["Precio"].get())
            stock = int(self.entries_agregar["Stock"].get())
            proveedor = self.entries_agregar["Proveedor"].get()
            producto = Producto(len(self.inventario.productos) + 1, nombre, descripcion, precio, stock, proveedor)
            self.inventario.agregar_producto(producto)
            self.base_datos.agregar_producto(producto)
            self.combo_modificar["values"] = ["Seleccionar"] + [p.nombre for p in self.inventario.productos]
            messagebox.showinfo("Éxito", "Producto agregado correctamente.")
        except ValueError:
            messagebox.showerror("Error", "Ingrese datos válidos para el producto.")

    def actualizar_datos_producto_seleccionado(self, event):
        selected_product = self.combo_modificar.get()
        if selected_product != "Seleccionar":
            producto = next((p for p in self.inventario.productos if p.nombre == selected_product), None)
            if producto:
                self.entries_modificar["Nombre del Producto"].delete(0, tk.END)
                self.entries_modificar["Nombre del Producto"].insert(0, producto.nombre)
                self.entries_modificar["Descripción"].delete(0, tk.END)
                self.entries_modificar["Descripción"].insert(0, producto.descripcion)
                self.entries_modificar["Precio"].delete(0, tk.END)
                self.entries_modificar["Precio"].insert(0, str(producto.precio))
                self.entries_modificar["Stock"].delete(0, tk.END)
                self.entries_modificar["Stock"].insert(0, str(producto.cantidad_stock))
                self.entries_modificar["Proveedor"].delete(0, tk.END)
                self.entries_modificar["Proveedor"].insert(0, producto.proveedor)

    def mostrar_acerca_de(self):
        messagebox.showinfo("Acerca de", "Sistema de Gestión de Inventarios\nVersión 1.0")

    def modificar_producto(self):
        # Requiere rol Admin
        if self.user_role != "Admin":
            messagebox.showerror("Error", "No tienes permisos para modificar (se requiere Admin).")
            return

        selected_product = self.combo_modificar.get()
        if selected_product != "Seleccionar":
            producto = next((p for p in self.inventario.productos if p.nombre == selected_product), None)
            if producto:
                nuevo_precio = self.entries_modificar["Precio"].get()
                nuevo_stock = self.entries_modificar["Stock"].get()
                nuevo_proveedor = self.entries_modificar["Proveedor"].get()
                nueva_descripcion = self.entries_modificar["Descripción"].get()
                if nuevo_precio and nuevo_stock and nuevo_proveedor and nueva_descripcion:
                    try:
                        nuevo_precio = float(nuevo_precio)
                        nuevo_stock = int(nuevo_stock)
                        producto.precio = nuevo_precio
                        producto.cantidad_stock = nuevo_stock
                        producto.proveedor = nuevo_proveedor
                        producto.descripcion = nueva_descripcion
                        self.base_datos.actualizar_producto(producto)
                        self.base_datos.cerrar_conexion()
                        self.base_datos = BaseDatos()
                        messagebox.showinfo("Éxito", "Producto modificado correctamente.")
                    except ValueError:
                        messagebox.showerror("Error", "Ingrese datos válidos para precio y stock.")
                else:
                    messagebox.showerror("Error", "Ingrese nuevo precio, stock, proveedor y descripción.")
            else:
                messagebox.showerror("Error", "Producto no encontrado.")
        else:
            messagebox.showerror("Error", "Seleccione un producto para modificar.")

    def cerrar_sesion(self):
        self.username = None
        self.user_role = None
        self.mostrar_ventana_login()
        self.aplicar_permisos_por_rol()
        messagebox.showinfo("Sesión", "Se ha cerrado la sesión.")

    def eliminar_producto(self):
        # Requiere rol Admin
        if self.user_role != "Admin":
            messagebox.showerror("Error", "No tienes permisos para eliminar (se requiere Admin).")
            return

        selected_product = self.combo_modificar.get()
        if selected_product != "Seleccionar":
            producto = next((p for p in self.inventario.productos if p.nombre == selected_product), None)
            if producto:
                self.inventario.eliminar_producto(producto)
                self.base_datos.eliminar_producto(producto)
                self.combo_modificar["values"] = ["Seleccionar"] + [p.nombre for p in self.inventario.productos]
                messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
            else:
                messagebox.showerror("Error", "Producto no encontrado.")
        else:
            messagebox.showerror("Error", "Seleccione un producto para eliminar.")

    def mostrar_ventana_login(self):
        # Ventana modal de login que solicita usuario y rol
        login = tk.Toplevel(self.root)
        login.title("Login")
        login.geometry("300x160")
        login.transient(self.root)
        login.grab_set()

        tk.Label(login, text="Usuario:", font=("Arial", 10)).pack(pady=(10,0))
        entry_user = tk.Entry(login, font=("Arial", 10))
        entry_user.pack(pady=5)

        tk.Label(login, text="Rol:", font=("Arial", 10)).pack(pady=(5,0))
        combo_rol = ttk.Combobox(login, values=["Admin", "Usuario"], state="readonly")
        combo_rol.current(1)
        combo_rol.pack(pady=5)

        def intentar_login():
            user = entry_user.get().strip()
            rol = combo_rol.get().strip()
            if not user:
                messagebox.showerror("Error", "Ingrese un nombre de usuario.", parent=login)
                return
            self.username = user
            self.user_role = rol
            login.grab_release()
            login.destroy()

        btn_login = tk.Button(login, text="Entrar", command=intentar_login)
        btn_login.pack(pady=8)
        self.root.wait_window(login)  # Espera hasta que la ventana modal se cierre

    def aplicar_permisos_por_rol(self):
        is_admin = (self.user_role == "Admin")
        try:
            if hasattr(self, 'boton_eliminar'):
                self.boton_eliminar.config(state=tk.NORMAL if is_admin else tk.DISABLED)
            if hasattr(self, 'boton_modificar'):
                self.boton_modificar.config(state=tk.NORMAL if is_admin else tk.DISABLED)
        except Exception:
            pass

    def crear_boton_mostrar_informe(self):
        self.boton_mostrar_informe = tk.Button(self.root, text="Mostrar Informe", command=self.mostrar_informe, font=("Arial", 12), bg="#333", fg="white")
        self.boton_mostrar_informe.pack(pady=10)

    def mostrar_informe(self):
        # Genera y muestra informe de inventarios en ventana con scrollbar
        informe = []
        try:
            informe = self.inventario.generar_informe()
        except Exception:
            informe = ["No hay datos disponibles para el informe."]
        mensaje = "\n\n".join(informe)

        ventana_informe = tk.Toplevel(self.root)
        ventana_informe.title("Informe de Inventarios")
        frame_mensaje = tk.Frame(ventana_informe)
        frame_mensaje.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_mensaje, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        txt_informe = tk.Text(frame_mensaje, yscrollcommand=scrollbar.set)
        txt_informe.pack(fill="both", expand=True)
        txt_informe.insert("1.0", mensaje)
        scrollbar.config(command=txt_informe.yview)


