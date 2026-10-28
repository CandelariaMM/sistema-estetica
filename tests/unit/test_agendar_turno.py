import pytest
from datetime import datetime
from src.domain.turno import Turno
from src.adapters.driven.memory_turno_repository import MemoryTurnoRepository
from src.ports.driving.agendar_turno_usecase import AgendarTurnoUseCase

def test_no_permite_agendar_dos_turnos_mismohorario_misma_profesional():
    repo = MemoryTurnoRepository()
    usecase = AgendarTurnoUseCase(repo)
    
    horario = datetime(2026, 8, 20, 15, 0)

    # Primer turno en Tunuyán con la profesional 1
    turno1 = Turno(
        id_turno=1, sucursal_id=1, cliente_id=1, profesional_id=1, servicio_id=1,
        fecha_hora=horario, detalles_servicio="Lifting",
        precio_actual_servicio=25000.0, costo_actual_servicio=5000.0
    )
    usecase.ejecutar(turno1)

    # Intento de segundo turno a la misma hora con la misma profesional
    turno_duplicado = Turno(
        id_turno=2, sucursal_id=1, cliente_id=2, profesional_id=1, servicio_id=2,
        fecha_hora=horario, detalles_servicio="Limpieza Facial",
        precio_actual_servicio=20000.0, costo_actual_servicio=3000.0
    )

    # Verificamos que lance la excepción/error esperado
    with pytest.raises(ValueError, match="La profesional ya tiene un turno agendado en ese horario."):
        usecase.ejecutar(turno_duplicado)