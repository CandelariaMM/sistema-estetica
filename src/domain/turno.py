from datetime import datetime
from typing import Optional

class Turno:
    def __init__(
        self,
        id_turno: int,
        sucursal_id: int,
        cliente_id: int,
        profesional_id: int,
        servicio_id: int,
        fecha_hora: datetime,
        detalles_servicio: str,
        precio_actual_servicio: float,
        costo_actual_servicio: float,
        monto_senia: float = 0.0,
        metodo_pago: Optional[str] = None,
        estado: str = "Agendado"
    ):
        if precio_actual_servicio < 0:
            raise ValueError("El precio cobrado no puede ser negativo")

        self.id_turno = id_turno
        self.sucursal_id = sucursal_id
        self.cliente_id = cliente_id
        self.profesional_id = profesional_id
        self.servicio_id = servicio_id
        self.fecha_hora = fecha_hora
        self.detalles_servicio = detalles_servicio
        
        # Congelamiento de valores para histórico financiero
        self.precio_cobrado = precio_actual_servicio
        self.costo_asociado = costo_actual_servicio
        
        self.monto_senia = monto_senia
        self.metodo_pago = metodo_pago
        self.estado = estado

    def calcular_monto_pendiente(self) -> float:
        """Devuelve lo que le falta pagar al cliente descontando la seña."""
        return max(0.0, self.precio_cobrado - self.monto_senia)

    def calcular_ganancia_neta(self) -> float:
        """Calcula el margen neto directo del servicio."""
        return self.precio_cobrado - self.costo_asociado