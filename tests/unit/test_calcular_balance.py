from datetime import datetime
from src.domain.turno import Turno
from src.domain.gasto import Gasto
from src.adapters.driven.sqlite_turno_repository import SqliteTurnoRepository
from src.adapters.driven.sqlite_gasto_repository import SqliteGastoRepository
from src.ports.driving.calcular_balance_usecase import CalcularBalanceUseCase

def test_calculo_balance_incluyendo_gastos_y_sueldos():
    # Usamos base de datos SQLite efímera en memoria para testing
    turno_repo = SqliteTurnoRepository(":memory:")
    gasto_repo = SqliteGastoRepository(":memory:")

    # Turno cobrado: $30.000 (Costo insumo: $5.000)
    turno_repo.guardar(Turno(
        id_turno=1, sucursal_id=1, cliente_id=1, profesional_id=1, servicio_id=1,
        fecha_hora=datetime.now(), detalles_servicio="Hollywood Peel",
        precio_actual_servicio=30000.0, costo_actual_servicio=5000.0, estado="Confirmado"
    ))

    # Carga de gastos: Sueldo por hora ($10.000) y Alquiler ($5.000)
    gasto_repo.registrar_gasto(Gasto(
        id_gasto=0, sucursal_id=1, concepto="Sueldo Empleada (6 hs)",
        monto=10000.0, fecha=datetime.now()
    ))
    gasto_repo.registrar_gasto(Gasto(
        id_gasto=0, sucursal_id=1, concepto="Alquiler diario",
        monto=5000.0, fecha=datetime.now()
    ))

    usecase = CalcularBalanceUseCase(turno_repo, gasto_repo)
    balance = usecase.ejecutar(sucursal_id=1)

    assert balance["ingreso_bruto"] == 30000.0
    assert balance["costos_directos"] == 5000.0
    assert balance["gastos_operativos"] == 15000.0
    assert balance["ganancia_neta_real"] == 10000.0  # 30k - 5k - 15k