import sqlite3
from datetime import datetime
from typing import List
from src.domain.gasto import Gasto
from src.ports.driven.gasto_repository import GastoRepository

class SqliteGastoRepository(GastoRepository):

    def __init__(self, db_path: str = "estetica.db"):
        self.db_path = db_path
        self._crear_tabla()

    def _obtener_conexion(self):
        return sqlite3.connect(self.db_path)

    def _crear_tabla(self):
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gastos (
                    id_gasto INTEGER PRIMARY KEY AUTOINCREMENT,
                    sucursal_id INTEGER NOT NULL,
                    concepto TEXT NOT NULL,
                    monto REAL NOT NULL,
                    fecha TEXT NOT NULL
                )
            """)
            conn.commit()

    def registrar_gasto(self, gasto: Gasto) -> Gasto:
        fecha_str = gasto.fecha.isoformat() if isinstance(gasto.fecha, datetime) else str(gasto.fecha)
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO gastos (sucursal_id, concepto, monto, fecha) VALUES (?, ?, ?, ?)",
                (gasto.sucursal_id, gasto.concepto, gasto.monto, fecha_str)
            )
            gasto.id_gasto = cursor.lastrowid
            conn.commit()
        return gasto

    def obtener_por_sucursal(self, sucursal_id: int) -> List[Gasto]:
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_gasto, sucursal_id, concepto, monto, fecha FROM gastos WHERE sucursal_id = ? ORDER BY id_gasto DESC",
                (sucursal_id,)
            )
            rows = cursor.fetchall()
            gastos = []
            for r in rows:
                try:
                    fecha_obj = datetime.fromisoformat(r[4])
                except Exception:
                    fecha_obj = datetime.now()

                gastos.append(
                    Gasto(
                        id_gasto=r[0],
                        sucursal_id=r[1],
                        concepto=r[2],
                        monto=r[3],
                        fecha=fecha_obj
                    )
                )
            return gastos