import tkinter as tk
from tkinter import ttk, messagebox 
import time
# Asegúrate de que bdd, inventario, producto, venta, y ventas están disponibles
from bdd import BaseDatos 
from inventario import Inventario 
from producto import Producto 
from venta import Venta 
from ventas import Ventas

class InterfazInventario:
    def __init__(self, root):
        self.base_datos = BaseDatos()
        self.inventario = Inventario()
        self.ventas = Ventas()
        self.cargar_productos_desde_db()
        
        # --- [INICIALIZACIÓN DE PROVEEDORES] ---
        self.lista_proveedores = [] 
        self.mapa_proveedores = {} # Mapa: Nombre -> ID
        self.nombres_proveedores = [""] 
        self.actualizar_combobox_proveedores() # Carga inicial de proveedores
        # ----------------------------------------
        
        self.username = None
        self.user_role = None 
        
        self.root = root
        self.root.title("Sistema de Gestión de Inventarios")
        self.root.geometry("800x450")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        self.crear_menu()
        self.crear_toolbar()

        self.pagina_agregar = ttk.Frame(self.notebook)
        self.pagina_modificar = ttk.Frame(self.notebook)
        self.pagina_estadisticas = ttk.Frame(self.notebook)
        self.pagina_ventas = ttk.Frame(self.notebook)
        self.pagina_proveedores = ttk.Frame(self.notebook) # <--- NUEVA PÁGINA

        self.notebook.add(self.pagina_agregar, text='Agregar Producto')
        self.notebook.add(self.pagina_modificar, text='Modificar Producto')
        self.notebook.add(self.pagina_estadisticas, text='Estadísticas')
        self.notebook.add(self.pagina_ventas, text='Ventas')
        self.notebook.add(self.pagina_proveedores, text='Gestión Proveedores') # <--- NUEVA PESTAÑA

        self.crear_interfaz_agregar_producto()
        self.crear_interfaz_modificar_producto()
        self.crear_boton_eliminar_producto() 
        self.crear_boton_mostrar_informe()
        self.crear_interfaz_estadisticas()
        self.crear_interfaz_agregar_venta()
        self.crear_boton_mostrar_ventas()
        self.crear_pagina_proveedores() # <--- LLAMADA A LA NUEVA FUNCIÓN

        self.mostrar_ventana_login()
        self.aplicar_permisos_por_rol()

    def cargar_productos_desde_db(self):
        productos_db = self.base_datos.obtener_productos()
        self.inventario.productos = productos_db

    # ------------------------------------------------------------------
    # --- FUNCIONES DE PROVEEDORES ---
    # ------------------------------------------------------------------

    def actualizar_combobox_proveedores(self):
        """Carga los proveedores de la BD y crea el mapeo ID<->Nombre."""
        self.lista_proveedores = self.base_datos.obtener_proveedores() # (ID, Nombre)
        self.mapa_proveedores = {nombre: id_ for id_, nombre in self.lista_proveedores}
        self.nombres_proveedores = [""] + list(self.mapa_proveedores.keys())
        
        if hasattr(self, 'combo_agregar_proveedor'):
            self.combo_agregar_proveedor['values'] = self.nombres_proveedores
        if hasattr(self, 'combo_modificar_proveedor'):
            self.combo_modificar_proveedor['values'] = self.nombres_proveedores

    def crear_pagina_proveedores(self):
        """Construye la interfaz para agregar nuevos proveedores."""
        tk.Label(self.pagina_proveedores, text="Agregar Nuevo Proveedor", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        campos = ["Nombre", "Teléfono", "Email", "Dirección"]
        self.entries_proveedor = {}
        
        for i, campo in enumerate(campos):
            tk.Label(self.pagina_proveedores, text=f"{campo}:", font=("Arial", 12)).grid(row=i+1, column=0, padx=5, pady=5, sticky='w')
            entry = tk.Entry(self.pagina_proveedores, width=35)
            entry.grid(row=i+1, column=1, padx=5, pady=5)
            self.entries_proveedor[campo] = entry

        self.boton_agregar_proveedor = tk.Button(self.pagina_proveedores, text="Agregar Proveedor", command=self.guardar_proveedor, font=("Arial", 12), bg="green", fg="white")
        self.boton_agregar_proveedor.grid(row=len(campos)+1, column=0, columnspan=2, pady=20)


    def guardar_proveedor(self):
        """Recoge los datos del formulario y llama al método de la BD para guardar."""
        if self.user_role != "Admin":
            messagebox.showwarning("Permiso Denegado", "Solo los administradores pueden agregar proveedores.")
            return

        nombre = self.entries_proveedor["Nombre"].get()
        telefono = self.entries_proveedor["Teléfono"].get()
        email = self.entries_proveedor["Email"].get()
        direccion = self.entries_proveedor["Dirección"].get()

        if nombre:
            if self.base_datos.agregar_proveedor(nombre, telefono, email, direccion):
                messagebox.showinfo("Éxito", f"Proveedor '{nombre}' agregado correctamente.")
                
                # Limpiar campos
                for entry in self.entries_proveedor.values():
                    entry.delete(0, tk.END)
                
                # Refrescar los Combobox de productos
                self.actualizar_combobox_proveedores() 
            # Si falla, el error lo muestra bdd.py
        else:
            messagebox.showwarning("Advertencia", "El nombre del proveedor es obligatorio.")

    # ------------------------------------------------------------------
    # --- INTERFAZ DE PRODUCTOS ---
    # ------------------------------------------------------------------

    def crear_interfaz_agregar_producto(self):
        etiquetas_agregar = ["Nombre del Producto", "Descripción", "Precio", "Stock", "Proveedor"]
        self.entries_agregar = {}
        for i, etiqueta in enumerate(etiquetas_agregar):
            tk.Label(self.pagina_agregar, text=etiqueta, font=("Arial", 12)).grid(row=i, column=0, padx=10, pady=5)
            
            if etiqueta == "Proveedor":
                # --- CAMBIO A COMBOBOX PARA PROVEEDOR ---
                self.combo_agregar_proveedor = ttk.Combobox(self.pagina_agregar, values=self.nombres_proveedores, state='readonly', font=("Arial", 12))
                self.combo_agregar_proveedor.grid(row=i, column=1, padx=10, pady=5)
                self.combo_agregar_proveedor.set(self.nombres_proveedores[0])
                self.entries_agregar[etiqueta] = self.combo_agregar_proveedor
            else:
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
        tk.Label(self.pagina_modificar, text=etiquetas_modificar[0], font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5) # Etiqueta de selección
        
        for i, etiqueta in enumerate(etiquetas_modificar[1:]):
            tk.Label(self.pagina_modificar, text=etiqueta, font=("Arial", 12)).grid(row=i + 1, column=0, padx=10, pady=5)
            
            if etiqueta == "Proveedor":
                # --- CAMBIO A COMBOBOX PARA PROVEEDOR ---
                self.combo_modificar_proveedor = ttk.Combobox(self.pagina_modificar, values=self.nombres_proveedores, state='readonly', font=("Arial", 12))
                self.combo_modificar_proveedor.grid(row=i + 1, column=1, padx=10, pady=5)
                self.entries_modificar[etiqueta] = self.combo_modificar_proveedor
            else:
                entry = tk.Entry(self.pagina_modificar, font=("Arial", 12))
                entry.grid(row=i + 1, column=1, padx=10, pady=5)
                self.entries_modificar[etiqueta] = entry
            
        self.boton_modificar = tk.Button(self.pagina_modificar, text="Modificar Producto", command=self.modificar_producto, font=("Arial", 12), bg="#008CBA", fg="white")
        self.boton_modificar.grid(row=len(etiquetas_modificar) + 1, column=0, columnspan=2, pady=10)

    # ------------------------------------------------------------------
    # --- MÉTODOS DE ACCIÓN ---
    # ------------------------------------------------------------------

    def agregar_producto(self):
        try:
            nombre = self.entries_agregar["Nombre del Producto"].get()
            descripcion = self.entries_agregar["Descripción"].get()
            precio = float(self.entries_agregar["Precio"].get())
            stock = int(self.entries_agregar["Stock"].get())
            
            # --- MANEJO DE PROVEEDOR POR ID ---
            nombre_proveedor = self.entries_agregar["Proveedor"].get()
            proveedor_id = self.mapa_proveedores.get(nombre_proveedor)
            
            if nombre_proveedor and proveedor_id is None:
                messagebox.showwarning("Advertencia", "Selecciona un proveedor válido.")
                return
            if not nombre_proveedor: 
                proveedor_id = None
            # -----------------------------------
            
            # Nota: Asumimos que el constructor de Producto fue actualizado para recibir proveedor_id
            producto = Producto(len(self.inventario.productos) + 1, nombre, descripcion, precio, stock, proveedor_id)
            self.inventario.agregar_producto(producto)
            self.base_datos.agregar_producto(producto)
            self.combo_modificar["values"] = ["Seleccionar"] + [p.nombre for p in self.inventario.productos]
            messagebox.showinfo("Éxito", "Producto agregado correctamente.")
            
            # Limpiar entradas
            for key in self.entries_agregar:
                if key != "Proveedor":
                    self.entries_agregar[key].delete(0, tk.END)
            self.entries_agregar["Proveedor"].set("")

        except ValueError:
            messagebox.showerror("Error", "Ingrese datos válidos para Precio y Stock.")


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
                
                # --- MANEJO DE PROVEEDOR POR ID (Muestra Nombre) ---
                # Asumo que producto.proveedor contiene el ID
                nombre_proveedor = next(
                    (nombre for id_, nombre in self.lista_proveedores if id_ == producto.proveedor), ""
                )
                self.entries_modificar["Proveedor"].set(nombre_proveedor)
                # ---------------------------------------------------


    def modificar_producto(self):
        if self.user_role != "Admin":
            messagebox.showerror("Error", "No tienes permisos para modificar (se requiere Admin).")
            return

        selected_product = self.combo_modificar.get()
        if selected_product != "Seleccionar":
            producto = next((p for p in self.inventario.productos if p.nombre == selected_product), None)
            if producto:
                nuevo_precio = self.entries_modificar["Precio"].get()
                nuevo_stock = self.entries_modificar["Stock"].get()
                nueva_descripcion = self.entries_modificar["Descripción"].get()
                
                # --- MANEJO DE PROVEEDOR POR ID ---
                nombre_proveedor_mod = self.entries_modificar["Proveedor"].get()
                nuevo_proveedor_id = self.mapa_proveedores.get(nombre_proveedor_mod)
                
                if nombre_proveedor_mod and nuevo_proveedor_id is None:
                    messagebox.showwarning("Advertencia", "Selecciona un proveedor válido.")
                    return
                if not nombre_proveedor_mod: 
                    nuevo_proveedor_id = None
                # -----------------------------------
                
                if nuevo_precio and nuevo_stock and nueva_descripcion:
                    try:
                        nuevo_precio = float(nuevo_precio)
                        nuevo_stock = int(nuevo_stock)
                        
                        producto.precio = nuevo_precio
                        producto.cantidad_stock = nuevo_stock
                        producto.proveedor = nuevo_proveedor_id # <--- Asigna el ID del proveedor
                        producto.descripcion = nueva_descripcion
                        
                        self.base_datos.actualizar_producto(producto)
                        messagebox.showinfo("Éxito", "Producto modificado correctamente.")
                        self.cargar_productos_desde_db() # Recargar datos
                        self.actualizar_combobox_proveedores() # Recargar combos

                    except ValueError:
                        messagebox.showerror("Error", "Ingrese datos válidos para precio y stock.")
                else:
                    messagebox.showerror("Error", "Todos los campos (precio, stock, proveedor, descripción) son obligatorios.")
            else:
                messagebox.showerror("Error", "Producto no encontrado.")
        else:
            messagebox.showerror("Error", "Seleccione un producto para modificar.")


    # El resto de métodos se mantienen igual (crear_menu, crear_toolbar, eliminar_producto, etc.)
    # ... (Copiar el resto de las funciones: crear_boton_eliminar_producto, crear_interfaz_estadisticas, crear_menu, crear_toolbar, crear_interfaz_agregar_venta, crear_boton_mostrar_ventas, agregar_venta, mostrar_ventas, mostrar_acerca_de, cerrar_sesion, eliminar_producto, mostrar_ventana_login, aplicar_permisos_por_rol, crear_boton_mostrar_informe, mostrar_informe)
    
    # --- MÉTODOS AUXILIARES Y DE CONFIGURACIÓN (Resto del código original) ---

    def crear_boton_eliminar_producto(self):
        self.boton_eliminar = tk.Button(self.pagina_modificar,
                                           text="Eliminar Producto",
                                           command=self.eliminar_producto,
                                           font=("Arial", 12),
                                           bg="#FF5733",
                                           fg="white")
        try:
            row_index = 8
            self.boton_eliminar.grid(row=row_index, column=0, columnspan=2, pady=10)
        except Exception:
            self.boton_eliminar.pack(pady=10)

    def crear_interfaz_estadisticas(self):
        total_productos_distintos = len(self.inventario.productos)
        total_productos = sum(producto.cantidad_stock for producto in self.inventario.productos)
        valor_total_inventario = sum(producto.precio * producto.cantidad_stock for producto in self.inventario.productos)
        precio_promedio = valor_total_inventario / total_productos if total_productos > 0 else 0
        
        etiquetas_estadisticas = [
            f"Cantidad productos distintos: {total_productos_distintos}",
            f"Cantidad Total de Productos: {total_productos}",
            f"Valor Total del Inventario: ${valor_total_inventario:.2f}",
            f"Precio Promedio de Productos: ${precio_promedio:.2f}"
        ]

        for i, etiqueta in enumerate(etiquetas_estadisticas):
            tk.Label(self.pagina_estadisticas, text=etiqueta, font=("Arial", 12)).grid(row=i, column=0, padx=10, pady=5, sticky='nsew')
        
        # self.root.after(1000, self.crear_interfaz_estadisticas) # Desactivado para evitar errores de recursión

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
        inventario_menu.add_command(label="Ir a: Gestión Proveedores", command=lambda: self.notebook.select(self.pagina_proveedores)) # Añadido
        menubar.add_cascade(label="Inventario", menu=inventario_menu)

        ventas_menu = tk.Menu(menubar, tearoff=0)
        ventas_menu.add_command(label="Mostrar Ventas", command=self.mostrar_ventas)
        menubar.add_cascade(label="Ventas", menu=ventas_menu)

        ayuda_menu = tk.Menu(menubar, tearoff=0)
        ayuda_menu.add_command(label="Acerca de", command=self.mostrar_acerca_de)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)

        self.root.config(menu=menubar)
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
        # El botón de ventas ya está en la barra de herramientas, lo eliminamos de aquí para evitar duplicados.
        # self.boton_mostrar_informe.pack(pady=10) 
    
    def agregar_venta(self):
        try:
            cant_art = self.entries_agregar_ventas["Cantidad Artículos"].get()
            medio_pago = self.entries_agregar_ventas["Medio de Pago"].get()
            total = float(self.entries_agregar_ventas["Total"].get())
            prodcutos = int(self.entries_agregar_ventas["Productos"].get())
            venta = Venta(len(self.ventas.ventas) + 1, cant_art, medio_pago, total, prodcutos)
            self.ventas.agregar_venta(venta)
            messagebox.showinfo("Éxito", "Venta agregada correctamente.")
        except ValueError:
            messagebox.showerror("Error", "Ingrese datos válidos para la venta.")

    def mostrar_ventas(self):
        informe = self.ventas.generar_informe_ventas()
        mensaje = "\n\n".join(informe)

        ventana_informe = tk.Toplevel(self.root)
        ventana_informe.title("Informe de Ventas")
        
        frame_mensaje = tk.Frame(ventana_informe)
        frame_mensaje.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_mensaje, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        txt_informe = tk.Text(frame_mensaje, yscrollcommand=scrollbar.set)
        txt_informe.pack(fill="both", expand=True)
        txt_informe.insert("1.0", mensaje)

        scrollbar.config(command=txt_informe.yview)

    def mostrar_acerca_de(self):
        messagebox.showinfo("Acerca de", "Sistema de Gestión de Inventarios\nVersión 1.0")

    def cerrar_sesion(self):
        self.username = None
        self.user_role = None
        self.mostrar_ventana_login()
        self.aplicar_permisos_por_rol()
        messagebox.showinfo("Sesión", "Se ha cerrado la sesión.")

    def eliminar_producto(self):
        if self.user_role != "Admin":
            messagebox.showerror("Error", "No tienes permisos para eliminar (se requiere Admin).")
            return

        selected_product = self.combo_modificar.get()
        if selected_product != "Seleccionar":
            producto = next((p for p in self.inventario.productos if p.nombre == selected_product), None)
            if producto:
                # La lógica de eliminación DEBE usar el método de BD que usa el ID
                if messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de eliminar {producto.nombre}?"):
                    self.base_datos.eliminar_producto(producto.producto_id)
                    self.inventario.eliminar_producto(producto)
                    self.cargar_productos_desde_db() # Recargar datos
                    self.combo_modificar["values"] = ["Seleccionar"] + [p.nombre for p in self.inventario.productos]
                    self.actualizar_combobox_proveedores() # Actualizar combos
                    messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
            else:
                messagebox.showerror("Error", "Producto no encontrado.")
        else:
            messagebox.showerror("Error", "Seleccione un producto para eliminar.")


    def mostrar_ventana_login(self):
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
        self.root.wait_window(login) 

    def aplicar_permisos_por_rol(self):
        is_admin = (self.user_role == "Admin")
        try:
            if hasattr(self, 'boton_eliminar'):
                self.boton_eliminar.config(state=tk.NORMAL if is_admin else tk.DISABLED)
            if hasattr(self, 'boton_modificar'):
                self.boton_modificar.config(state=tk.NORMAL if is_admin else tk.DISABLED)
            if hasattr(self, 'boton_agregar'): # Botón en la página de agregar producto
                self.boton_agregar.config(state=tk.NORMAL if is_admin else tk.DISABLED)
            if hasattr(self, 'boton_agregar_proveedor'): # Botón en la página de proveedores
                self.boton_agregar_proveedor.config(state=tk.NORMAL if is_admin else tk.DISABLED)
        except Exception:
            pass

    def crear_boton_mostrar_informe(self):
        self.boton_mostrar_informe = tk.Button(self.root, text="Mostrar Informe", command=self.mostrar_informe, font=("Arial", 12), bg="#333", fg="white")
        # El botón de informe ya está en la barra de herramientas, lo eliminamos de aquí para evitar duplicados.
        # self.boton_mostrar_informe.pack(pady=10)

    def mostrar_informe(self):
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