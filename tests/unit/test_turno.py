import pytest
from datetime import datetime
from src.domain.turno import Turno

def test_creacion_turno_congela_precio_y_calcula_pendiente():
    # Arrange / Dado que...
    fecha = datetime(2026, 8, 25, 15, 0)
    
    # Act / Cuando creamos un turno con precio $25.000 y seña de $5.000
    turno = Turno(
        id_turno=1,
        sucursal_id=1,      # Tunuyán
        cliente_id=10,
        profesional_id=2,
        servicio_id=5,
        fecha_hora=fecha,
        detalles_servicio="Limpieza facial premium",
        precio_actual_servicio=25000.0,
        costo_actual_servicio=5000.0,
        monto_senia=5000.0,
        metodo_pago="Transferencia"
    )

    # Assert / Entonces verificamos...
    assert turno.precio_cobrado == 25000.0
    assert turno.calcular_monto_pendiente() == 20000.0
    assert turno.calcular_ganancia_neta() == 20000.0

def test_no_permite_precios_negativos():
    # Verifica que el dominio proteja los datos inválidos
    with pytest.raises(ValueError, match="El precio cobrado no puede ser negativo"):
        Turno(
            id_turno=2,
            sucursal_id=1,
            cliente_id=10,
            profesional_id=2,
            servicio_id=5,
            fecha_hora=datetime.now(),
            detalles_servicio="Test",
            precio_actual_servicio=-1000.0,
            costo_actual_servicio=100.0
        )