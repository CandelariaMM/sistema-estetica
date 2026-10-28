from datetime import datetime

class Gasto:
    def __init__(
        self,
        id_gasto: int,
        sucursal_id: int,
        concepto: str,  # Ej: "Alquiler", "Insumos", "Sueldo Empleada"
        monto: float,
        fecha: datetime
    ):
        if monto <= 0:
            raise ValueError("El monto del gasto debe ser mayor a cero")

        self.id_gasto = id_gasto
        self.sucursal_id = sucursal_id
        self.concepto = concepto
        self.monto = monto
        self.fecha = fecha