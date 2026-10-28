class Servicio:
    def __init__(self, id_servicio: int, nombre: str, precio_base: float, costo_base: float, duracion_base_minutos: int = 30):
        if not nombre.strip():
            raise ValueError("El nombre del servicio no puede estar vacío")
        if precio_base < 0:
            raise ValueError("El precio del servicio no puede ser negativo")
        
        self.id_servicio = id_servicio
        self.nombre = nombre
        self.precio_base = precio_base
        self.costo_base = costo_base
        self.duracion_base_minutos = duracion_base_minutos