from datetime import datetime
from src.domain.turno import Turno
from src.adapters.driven.sqlite_turno_repository import SqliteTurnoRepository

def test_guardar_y_recuperar_turno_en_sqlite():
    # Usamos :memory: para que no cree un archivo físico durante el test
    repo = SqliteTurnoRepository(db_path=":memory:")

    turno = Turno(
        id_turno=1,
        sucursal_id=1,
        cliente_id=5,
        profesional_id=2,
        servicio_id=3,
        fecha_hora=datetime(2026, 9, 20, 10, 0),
        detalles_servicio="Hollywood Peel",
        precio_actual_servicio=30000.0,
        costo_actual_servicio=5000.0,
        monto_senia=5000.0,
        metodo_pago="Efectivo"
    )

    repo.guardar(turno)
    turno_guardado = repo.obtener_por_id(1)

    assert turno_guardado is not None
    assert turno_guardado.detalles_servicio == "Hollywood Peel"
    assert turno_guardado.precio_cobrado == 30000.0