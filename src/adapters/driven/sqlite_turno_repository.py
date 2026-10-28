import sqlite3
from typing import List, Optional
from datetime import datetime
from src.domain.turno import Turno
from src.ports.driven.turno_repository import TurnoRepository

class SqliteTurnoRepository(TurnoRepository):

    def __init__(self, db_path: str = "estetica.db"):
        self.db_path = db_path
        # Si es en memoria, mantenemos la conexion abierta durante la vida del repositorio
        if self.db_path == ":memory:":
            self._conn = sqlite3.connect(":memory:")
        else:
            self._conn = None
            
        self._crear_tabla()

    def _obtener_conexion(self):
        if self.db_path == ":memory:":
            return self._conn
        return sqlite3.connect(self.db_path)

    def _cerrar_conexion(self, conn):
        # Solo cerramos la conexion si es un archivo en disco, no si es en memoria RAM
        if self.db_path != ":memory:":
            conn.close()

    def _crear_tabla(self):
        conn = self._obtener_conexion()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS turnos (
                    id_turno INTEGER PRIMARY KEY,
                    sucursal_id INTEGER NOT NULL,
                    cliente_id INTEGER NOT NULL,
                    profesional_id INTEGER NOT NULL,
                    servicio_id INTEGER NOT NULL,
                    fecha_hora TEXT NOT NULL,
                    detalles_servicio TEXT,
                    precio_cobrado REAL NOT NULL,
                    costo_asociado REAL NOT NULL,
                    monto_senia REAL DEFAULT 0.0,
                    metodo_pago TEXT,
                    estado TEXT NOT NULL
                )
            """)
            conn.commit()
        finally:
            self._cerrar_conexion(conn)

    def guardar(self, turno: Turno) -> Turno:
        fecha_str = turno.fecha_hora.isoformat() if isinstance(turno.fecha_hora, datetime) else str(turno.fecha_hora)
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            if getattr(turno, "id_turno", 0) == 0:
                cursor.execute("""
                    INSERT INTO turnos (
                        sucursal_id, cliente_id, profesional_id, servicio_id,
                        fecha_hora, detalles_servicio, precio_cobrado, costo_asociado,
                        monto_senia, metodo_pago, estado
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    turno.sucursal_id, turno.cliente_id, turno.profesional_id, turno.servicio_id,
                    fecha_str, turno.detalles_servicio, turno.precio_cobrado, turno.costo_asociado,
                    turno.monto_senia, turno.metodo_pago, turno.estado
                ))
                turno.id_turno = cursor.lastrowid
            else:
                cursor.execute("""
                    INSERT OR REPLACE INTO turnos (
                        id_turno, sucursal_id, cliente_id, profesional_id, servicio_id,
                        fecha_hora, detalles_servicio, precio_cobrado, costo_asociado,
                        monto_senia, metodo_pago, estado
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    turno.id_turno, turno.sucursal_id, turno.cliente_id, turno.profesional_id, turno.servicio_id,
                    fecha_str, turno.detalles_servicio, turno.precio_cobrado, turno.costo_asociado,
                    turno.monto_senia, turno.metodo_pago, turno.estado
                ))
            conn.commit()
        return turno

    def obtener_por_id(self, id_turno: int) -> Optional[Turno]:
        conn = self._obtener_conexion()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM turnos WHERE id_turno = ?", (id_turno,))
            row = cursor.fetchone()
            if row:
                return self._mapear_fila_a_turno(row)
        finally:
            self._cerrar_conexion(conn)
        return None

    def obtener_por_sucursal(self, sucursal_id: int) -> List[Turno]:
        conn = self._obtener_conexion()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM turnos WHERE sucursal_id = ? ORDER BY fecha_hora ASC", (sucursal_id,))
            rows = cursor.fetchall()
            return [self._mapear_fila_a_turno(row) for row in rows]
        finally:
            self._cerrar_conexion(conn)

    def _mapear_fila_a_turno(self, row) -> Turno:
        return Turno(
            id_turno=row[0],
            sucursal_id=row[1],
            cliente_id=row[2],
            profesional_id=row[3],
            servicio_id=row[4],
            fecha_hora=datetime.fromisoformat(row[5]),
            detalles_servicio=row[6],
            precio_actual_servicio=row[7],
            costo_actual_servicio=row[8],
            monto_senia=row[9],
            metodo_pago=row[10],
            estado=row[11]
        )

    def eliminar_turno(self, id_turno: int) -> bool:
        """Elimina permanentemente un turno de la base de datos por su ID."""
        conn = self._obtener_conexion()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM turnos WHERE id_turno = ?", (id_turno,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            self._cerrar_conexion(conn) 