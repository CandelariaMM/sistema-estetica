from datetime import datetime
from src.domain.turno import Turno
from src.adapters.driven.sqlite_turno_repository import SqliteTurnoRepository

def test_guardar_y_filtrar_turnos_por_sucursal():
    # Usamos SQLite en memoria para la prueba
    repo = SqliteTurnoRepository(":memory:")

    # Turno 1 en Tunuyán (ID: 1)
    turno_tunuyan = Turno(
        id_turno=1,
        sucursal_id=1,
        cliente_id=10,
        profesional_id=2,
        servicio_id=5,
        fecha_hora=datetime.now(),
        detalles_servicio="Lifting de pestañas",
        precio_actual_servicio=25000.0,
        costo_actual_servicio=5000.0
    )

    # Turno 2 en Tupungato (ID: 2)
    turno_tupungato = Turno(
        id_turno=2,
        sucursal_id=2,
        cliente_id=11,
        profesional_id=2,
        servicio_id=5,
        fecha_hora=datetime.now(),
        detalles_servicio="Depilación Definitiva",
        precio_actual_servicio=30000.0,
        costo_actual_servicio=8000.0
    )

    repo.guardar(turno_tunuyan)
    repo.guardar(turno_tupungato)

    turnos_tunuyan = repo.obtener_por_sucursal(1)
    assert len(turnos_tunuyan) == 1
    assert turnos_tunuyan[0].detalles_servicio == "Lifting de pestañas"