from producto import Producto 

# Clase para representar un artículo específico dentro de la venta (fila de venta_items)
class VentaItem:
    def __init__(self, producto_id: int, nombre_producto: str, cantidad: int, precio_unitario: float):
        self.producto_id = producto_id
        self.nombre_producto = nombre_producto # Para visualización
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal = self._calcular_subtotal()

    def _calcular_subtotal(self):
        """Calcula el subtotal para este artículo."""
        return round(self.cantidad * self.precio_unitario, 2)

    def to_dict(self):
        """Retorna un diccionario útil para la inserción en la base de datos o visualización."""
        return {
            'producto_id': self.producto_id,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'subtotal': self.subtotal
        }

# Clase para representar el encabezado de la venta (fila de ventas)
class Venta:
    def __init__(self, medio_pago: str = 'Efectivo', usuario_id: int = None, items: list[VentaItem] = None, id_venta: int = None):
        # Campos que se mapean directamente a la tabla 'ventas'
        self.id = id_venta
        self.medio_pago = medio_pago
        self.usuario_id = usuario_id
        
        # Lista de objetos VentaItem
        self._items: list[VentaItem] = items if items is not None else []
        
        # El total se calcula dinámicamente
        self._total = self._calcular_total()

    def agregar_item(self, item: VentaItem):
        """Añade un artículo a la lista de items de la venta."""
        self._items.append(item)
        self._total = self._calcular_total() # Recalcula el total

    def _calcular_total(self) -> float:
        """Calcula el total general de la venta sumando los subtotales de todos los items."""
        return round(sum(item.subtotal for item in self._items), 2)

    # PROPIEDAD TOTAL (Solo lectura, ya que se calcula)
    @property
    def total(self):
        """Retorna el total calculado de la venta."""
        return self._calcular_total()
    
    # PROPIEDAD ITEMS
    @property
    def items(self):
        """Retorna la lista de artículos de la venta."""
        return self._items
    
    @items.setter
    def items(self, nuevos_items: list[VentaItem]):
        """Establece nuevos items y recalcula el total."""
        self._items = nuevos_items
        self._total = self._calcular_total()

    # PROPIEDAD CANTIDAD DE ARTÍCULOS (Solo lectura, se calcula)
    @property
    def cant_articulos(self):
        """Retorna la suma de las cantidades de todos los items."""
        return sum(item.cantidad for item in self._items)

    def __repr__(self):
        """Representación amigable del objeto Venta."""
        return f"Venta(ID={self.id}, Total={self.total}, Items={len(self._items)})"

    def obtener_resumen(self):
        """Genera un resumen detallado de la venta."""
        resumen = f"--- Resumen de Venta #{self.id if self.id else 'Nueva'} ---\n"
        resumen += f"Total: {self.total}\n"
        resumen += f"Artículos: {self.cant_articulos}\n"
        resumen += f"Pago: {self.medio_pago}\n"
        resumen += "\nDetalle de Productos:\n"
        for item in self.items:
            resumen += f"- {item.nombre_producto} (x{item.cantidad}) @ {item.precio_unitario} = {item.subtotal}\n"
        return resumen

# Ejemplo de uso:
# Si el precio_unitario viene de la BD al cargar el producto.
if __name__ == '__main__':
    # 1. Crear los artículos de la venta (VentaItem)
    item1 = VentaItem(producto_id=1, nombre_producto="Pendrive 64GB", cantidad=2, precio_unitario=20000.0)
    item2 = VentaItem(producto_id=4, nombre_producto="SSD Crucial 500GB", cantidad=1, precio_unitario=79990.0)

    # 2. Crear la venta (Venta) y añadir los artículos
    nueva_venta = Venta(medio_pago='Tarjeta de Crédito', usuario_id=101)
    nueva_venta.agregar_item(item1)
    nueva_venta.agregar_item(item2)
    
    # 3. Verificación de cálculos
    print(nueva_venta.obtener_resumen())
    print(f"Total calculado automáticamente: {nueva_venta.total}")
    print(f"Items en la venta: {len(nueva_venta.items)}")