from datetime import datetime

class CalcularBalanceUseCase:
    def __init__(self, turno_repository, gasto_repository):
        self.turno_repository = turno_repository
        self.gasto_repository = gasto_repository

    def ejecutar(self, sucursal_id: int):
        ahora = datetime.now()
        turnos_sucursal = self.turno_repository.obtener_por_sucursal(sucursal_id)
        
        # Turnos computables: NO cancelados y que hayan transcurrido O estén confirmados
        turnos_computables = [
            t for t in turnos_sucursal 
            if getattr(t, "estado", "") != "Cancelado" and (
                getattr(t, "fecha_hora", ahora) <= ahora or getattr(t, "estado", "") == "Confirmado"
            )
        ]

        ingreso_bruto = sum(getattr(t, "precio_cobrado", getattr(t, "precio_actual_servicio", 0.0)) for t in turnos_computables)
        costos_directos = sum(getattr(t, "costo_asociado", getattr(t, "costo_actual_servicio", 0.0)) for t in turnos_computables)

        gastos_sucursal = self.gasto_repository.obtener_por_sucursal(sucursal_id)
        gastos_operativos = sum(getattr(g, "monto", 0.0) for g in gastos_sucursal)

        margen_directo = ingreso_bruto - costos_directos
        ganancia_neta_real = margen_directo - gastos_operativos

        detalle_turnos = [
            {
                "id_turno": getattr(t, "id_turno", 0),
                "fecha_hora": getattr(t, "fecha_hora", ahora).isoformat() if hasattr(getattr(t, "fecha_hora", None), "isoformat") else str(getattr(t, "fecha_hora", "")),
                "detalles_servicio": getattr(t, "detalles_servicio", "Servicio"),
                "precio": getattr(t, "precio_cobrado", getattr(t, "precio_actual_servicio", 0.0)),
                "costo": getattr(t, "costo_asociado", getattr(t, "costo_actual_servicio", 0.0))
            }
            for t in turnos_computables
        ]

        detalle_gastos = [
            {
                "id_gasto": getattr(g, "id_gasto", 0),
                "concepto": getattr(g, "concepto", "Gasto"),
                "monto": getattr(g, "monto", 0.0),
                "fecha": getattr(g, "fecha", ahora).isoformat() if hasattr(getattr(g, "fecha", None), "isoformat") else str(getattr(g, "fecha", ""))
            }
            for g in gastos_sucursal
        ]

        return {
            "sucursal_id": sucursal_id,
            "ingreso_bruto": ingreso_bruto,
            "costos_directos": costos_directos,
            "margen_directo": margen_directo,
            "gastos_operativos": gastos_operativos,
            "ganancia_neta_real": ganancia_neta_real,
            "cantidad_turnos_realizados": len(turnos_computables),
            "detalle_turnos": detalle_turnos,
            "detalle_gastos": detalle_gastos
        }