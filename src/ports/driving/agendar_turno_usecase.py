from datetime import datetime
from src.domain.turno import Turno
from src.ports.driven.turno_repository import TurnoRepository

class AgendarTurnoUseCase:

    def __init__(self, turno_repo: TurnoRepository):
        self.turno_repo = turno_repo

    def ejecutar(self, turno_nuevo: Turno) -> Turno:
        """Valida que no haya superposición de horario y guarda el turno."""
        turnos_existentes = self.turno_repo.obtener_por_sucursal(turno_nuevo.sucursal_id)

        for turno in turnos_existentes:
            # Si es la misma profesional, el mismo día/hora y no está cancelado
            if (
                turno.profesional_id == turno_nuevo.profesional_id
                and turno.fecha_hora == turno_nuevo.fecha_hora
                and turno.estado != "Cancelado"
            ):
                raise ValueError("La profesional ya tiene un turno agendado en ese horario.")

        return self.turno_repo.guardar(turno_nuevo)