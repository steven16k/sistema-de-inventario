import mysql.connector
from tkinter import messagebox 
from producto import Producto 

MYSQL_CONFIG = {
    'host': 'localhost',      
    'user': 'root',           
    'password': '', 
    'database': 'sistema_inventario'
}

class BaseDatos:
    def __init__(self):
        self.conexion = None
        self.cursor = None
        self._conectar()

    def _conectar(self):
        """Intenta establecer la conexión con MySQL."""
        try:
            self.conexion = mysql.connector.connect(**MYSQL_CONFIG)
            self.cursor = self.conexion.cursor()
        except mysql.connector.Error as err:
            messagebox.showerror("Error de Conexión a MySQL", 
                                 f"No se pudo conectar a la base de datos MySQL:\n{err}\n"
                                 f"Por favor, revisa la configuración en base_datos_mysql.py y asegúrate de que MySQL esté activo.")
            raise ConnectionError("Falló la conexión a MySQL.")

    
    def obtener_productos(self):
        self.cursor.execute("SELECT id, nombre, descripcion, precio, cantidad_stock, proveedor_id FROM productos")
        rows = self.cursor.fetchall() 
        return [Producto(*row) for row in rows] 

    def agregar_producto(self, producto):
        try:
            self.cursor.execute('''
                INSERT INTO productos (nombre, descripcion, precio, cantidad_stock, proveedor_id)
                VALUES (%s, %s, %s, %s, %s)
            ''', (producto.nombre, producto.descripcion, producto.precio, producto.cantidad_stock, producto.proveedor_id))
            self.conexion.commit() 
        except mysql.connector.Error as error:
            messagebox.showerror("Error en base de datos", f"No se pudo agregar el producto: {error}")

    def eliminar_producto(self, producto):
        try:
            self.cursor.execute('''
                 DELETE FROM productos WHERE id=%s
            ''', (producto.id,))
            self.conexion.commit()
        except mysql.connector.Error as error:
            messagebox.showerror("Error en base de datos", f"No se pudo eliminar el producto: {error}")

    def actualizar_producto(self, producto):
        try:
            self.cursor.execute('''
                 UPDATE productos SET nombre=%s, descripcion=%s, precio=%s, cantidad_stock=%s, proveedor_id=%s WHERE id=%s
            ''', (producto.nombre, producto.descripcion, producto.precio, producto.cantidad_stock, producto.proveedor_id, producto.id))
            self.conexion.commit() 
        except mysql.connector.Error as error:
            messagebox.showerror("Error en base de datos", f"No se pudo actualizar el producto: {error}")
    
    def buscar_productos_por_nombre(self, nombre):
        try:
            self.cursor.execute("SELECT id, nombre, descripcion, precio, cantidad_stock, proveedor_id FROM productos WHERE nombre LIKE %s", ('%' + nombre + '%',))
            rows = self.cursor.fetchall()
            return [Producto(*row) for row in rows]
        except mysql.connector.Error as error:
            messagebox.showerror("Error en base de datos", f"No se pudo buscar productos por nombre: {error}")
            return []
    
    def buscar_productos_por_proveedor(self, proveedor_id):
        try:
            self.cursor.execute("SELECT id, nombre, descripcion, precio, cantidad_stock, proveedor_id FROM productos WHERE proveedor_id=%s", (proveedor_id,))
            rows = self.cursor.fetchall()
            return [Producto(*row) for row in rows]
        except mysql.connector.Error as error:
            messagebox.showerror("Error en base de datos", f"No se pudo buscar productos por proveedor: {error}")
            return []

    def buscar_producto_por_id(self, producto_id):
        try:
            self.cursor.execute("SELECT id, nombre, descripcion, precio, cantidad_stock, proveedor_id FROM productos WHERE id=%s", (producto_id,))
            row = self.cursor.fetchone()
            if row:
                return Producto(*row)
            return None
        except mysql.connector.Error as error:
            messagebox.showerror("Error en base de datos", f"No se pudo buscar producto por ID: {error}")
            return None
    
    def cerrar_conexion(self):
        if self.conexion and self.conexion.is_connected():
            self.cursor.close()
            self.conexion.close()