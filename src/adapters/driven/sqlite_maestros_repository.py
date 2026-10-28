import sqlite3
from typing import List, Optional
from src.domain.cliente import Cliente
from src.domain.profesional import Profesional
from src.domain.servicio import Servicio
from src.ports.driven.maestros_repository import MaestrosRepository

class SqliteMaestrosRepository(MaestrosRepository):

    def __init__(self, db_path: str = "estetica.db"):
        self.db_path = db_path
        self._crear_tablas()

    def _obtener_conexion(self):
        return sqlite3.connect(self.db_path)

    def _crear_tablas(self):
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    telefono TEXT NOT NULL,
                    email TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profesionales (
                    id_profesional INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    especialidad TEXT NOT NULL,
                    sucursal_id INTEGER NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS servicios (
                    id_servicio INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    precio_base REAL NOT NULL,
                    costo_base REAL NOT NULL,
                    duracion_base_minutos INTEGER DEFAULT 30
                )
            """)
            # Intentar agregar la columna duracion_base_minutos si la tabla ya existia previamente
            try:
                cursor.execute("ALTER TABLE servicios ADD COLUMN duracion_base_minutos INTEGER DEFAULT 30")
            except sqlite3.OperationalError:
                pass  # La columna ya existe
            conn.commit()

    # --- CLIENTES ---
    def guardar_cliente(self, cliente: Cliente) -> Cliente:
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO clientes (nombre, telefono, email) VALUES (?, ?, ?)",
                (cliente.nombre, cliente.telefono, cliente.email)
            )
            cliente.id_cliente = cursor.lastrowid
            conn.commit()
        return cliente

    def listar_clientes(self) -> List[Cliente]:
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_cliente, nombre, telefono, email FROM clientes ORDER BY nombre ASC")
            rows = cursor.fetchall()
            return [Cliente(id_cliente=r[0], nombre=r[1], telefono=r[2], email=r[3]) for r in rows]

    def modificar_cliente(self, id_cliente: int, nombre: str, telefono: str, email: str) -> bool:
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clientes SET nombre = ?, telefono = ?, email = ? WHERE id_cliente = ?",
                (nombre, telefono, email, id_cliente)
            )
            conn.commit()
            return cursor.rowcount > 0

    def eliminar_cliente(self, id_cliente: int) -> bool:
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE id_cliente = ?", (id_cliente,))
            conn.commit()
            return cursor.rowcount > 0

    # --- PROFESIONALES ---
    def guardar_profesional(self, profesional: Profesional) -> Profesional:
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO profesionales (nombre, especialidad, sucursal_id) VALUES (?, ?, ?)",
                (profesional.nombre, profesional.especialidad, profesional.sucursal_id)
            )
            profesional.id_profesional = cursor.lastrowid
            conn.commit()
        return profesional

    def listar_profesionales(self) -> List[Profesional]:
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_profesional, nombre, especialidad, sucursal_id FROM profesionales ORDER BY nombre ASC")
            rows = cursor.fetchall()
            return [Profesional(id_profesional=r[0], nombre=r[1], especialidad=r[2], sucursal_id=r[3]) for r in rows]

    def modificar_profesional(self, id_profesional: int, nombre: str, especialidad: str, sucursal_id: int) -> bool:
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE profesionales SET nombre = ?, especialidad = ?, sucursal_id = ? WHERE id_profesional = ?",
                (nombre, especialidad, sucursal_id, id_profesional)
            )
            conn.commit()
            return cursor.rowcount > 0

    def eliminar_profesional(self, id_profesional: int) -> bool:
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM profesionales WHERE id_profesional = ?", (id_profesional,))
            conn.commit()
            return cursor.rowcount > 0

    # --- SERVICIOS ---
    def guardar_servicio(self, servicio: Servicio) -> Servicio:
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO servicios (nombre, precio_base, costo_base, duracion_base_minutos) VALUES (?, ?, ?, ?)",
                (servicio.nombre, servicio.precio_base, servicio.costo_base, servicio.duracion_base_minutos)
            )
            servicio.id_servicio = cursor.lastrowid
            conn.commit()
        return servicio

    def listar_servicios(self) -> List[Servicio]:
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_servicio, nombre, precio_base, costo_base, duracion_base_minutos FROM servicios ORDER BY nombre ASC")
            rows = cursor.fetchall()
            return [
                Servicio(
                    id_servicio=r[0], 
                    nombre=r[1], 
                    precio_base=r[2], 
                    costo_base=r[3], 
                    duracion_base_minutos=r[4] if len(r) > 4 and r[4] else 30
                ) for r in rows
            ]

    def modificar_servicio(self, id_servicio: int, nombre: str, precio_base: float, costo_base: float, duracion_base_minutos: int) -> bool:
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE servicios SET nombre = ?, precio_base = ?, costo_base = ?, duracion_base_minutos = ? WHERE id_servicio = ?",
                (nombre, precio_base, costo_base, duracion_base_minutos, id_servicio)
            )
            conn.commit()
            return cursor.rowcount > 0

    def eliminar_servicio(self, id_servicio: int) -> bool:
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM servicios WHERE id_servicio = ?", (id_servicio,))
            conn.commit()
            return cursor.rowcount > 0