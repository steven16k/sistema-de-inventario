# producto.py

# Clase Producto
class Producto:
    def __init__(self, producto_id, nombre, descripcion, precio, cantidad_stock, proveedor_id):
        self.producto_id = producto_id
        self._nombre = nombre
        self._descripcion = descripcion
        self._precio = precio
        self._cantidad_stock = cantidad_stock
        self._proveedor_id = proveedor_id # <--- CAMBIO CLAVE

    # NOMBRE
    @property
    def nombre(self):
        return self._nombre
    @nombre.setter
    def nombre(self, nuevo_nombre):
        self._nombre = nuevo_nombre

    # DESCRIPCION
    @property
    def descripcion(self):
        return self._descripcion
    @descripcion.setter
    def descripcion(self, nueva_descripcion):
        self._descripcion = nueva_descripcion
    
    # PRECIO  
    @property
    def precio(self):
        return self._precio
    @precio.setter
    def precio(self, nuevo_precio):
        self._precio = nuevo_precio
    
    # STOCK
    @property
    def cantidad_stock(self):
        return self._cantidad_stock
    @cantidad_stock.setter
    def cantidad_stock(self, nuevo_stock):
        self._cantidad_stock = nuevo_stock

    # PROVEEDOR_ID (Se cambió 'proveedor' por 'proveedor_id')
    @property
    def proveedor_id(self): # <--- CAMBIO CLAVE
        return self._proveedor_id
    @proveedor_id.setter
    def proveedor_id(self, nuevo_proveedor_id): # <--- CAMBIO CLAVE
        self._proveedor_id = nuevo_proveedor_id

    # OBTENER DETALLES
    def obtener_detalles(self):
        detalles = f"ID: {self.producto_id}\nNombre: {self.nombre}\nDescripción: {self.descripcion}\n"
        detalles += f"Precio: {self.precio}\nStock: {self.cantidad_stock}\nProveedor ID: {self.proveedor_id}" 
        return detalles