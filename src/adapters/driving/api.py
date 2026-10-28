import os
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# --- IMPORTACIONES DE DOMINIO ---
from src.domain.turno import Turno
from src.domain.cliente import Cliente
from src.domain.profesional import Profesional
from src.domain.servicio import Servicio
from src.domain.gasto import Gasto

# --- IMPORTACIONES DE ADAPTADORES DE PERSISTENCIA ---
from src.adapters.driven.sqlite_turno_repository import SqliteTurnoRepository
from src.adapters.driven.sqlite_maestros_repository import SqliteMaestrosRepository
from src.adapters.driven.sqlite_gasto_repository import SqliteGastoRepository

# --- IMPORTACIONES DE CASOS DE USO ---
from src.ports.driving.agendar_turno_usecase import AgendarTurnoUseCase
from src.ports.driving.calcular_balance_usecase import CalcularBalanceUseCase
from src.ports.driving.generar_notificacion_whatsapp_usecase import GenerarNotificacionWhatsAppUseCase
from src.ports.driving.buscar_disponibilidad_usecase import BuscarDisponibilidadUseCase

# --- CONFIGURACIÓN PRINCIPAL DE FASTAPI Y TEMPLATES ---
app = FastAPI(title="Sistema de Gestión - Estética")



templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


# --- INICIALIZACIÓN DE REPOSITORIOS Y CASOS DE USO ---
turno_repo = SqliteTurnoRepository("estetica.db")
maestros_repo = SqliteMaestrosRepository("estetica.db")
gasto_repo = SqliteGastoRepository("estetica.db")

agendar_usecase = AgendarTurnoUseCase(turno_repo)
balance_usecase = CalcularBalanceUseCase(turno_repo, gasto_repo)
notificacion_usecase = GenerarNotificacionWhatsAppUseCase(turno_repo, maestros_repo)
disponibilidad_usecase = BuscarDisponibilidadUseCase(turno_repo, maestros_repo)


# --- ESQUEMAS PYDANTIC (ENTRADA DE DATOS REST) ---
class TurnoSchema(BaseModel):
    id_turno: int
    sucursal_id: int
    cliente_id: int
    profesional_id: int
    servicio_id: int
    fecha_hora: datetime
    detalles_servicio: str
    precio_actual_servicio: float
    costo_actual_servicio: float
    monto_senia: float = 0.0
    metodo_pago: Optional[str] = "A confirmar al asistir"
    estado: Optional[str] = "En espera"

class ClienteSchema(BaseModel):
    nombre: str
    telefono: str
    email: Optional[str] = ""

class ProfesionalSchema(BaseModel):
    nombre: str
    especialidad: str
    sucursal_id: int

class ServicioSchema(BaseModel):
    nombre: str
    precio_base: float
    costo_base: float
    duracion_base_minutos: Optional[int] = 30

class GastoSchema(BaseModel):
    sucursal_id: int
    concepto: str
    monto: float


# --- 1. RUTAS DE NAVEGACIÓN Y VISTAS HTML (FRONTEND) ---

@app.get("/", response_class=HTMLResponse)
@app.get("/turnos-view", response_class=HTMLResponse)
def vista_turnos(request: Request):
    return templates.TemplateResponse(request=request, name="turnos.html", context={"active_tab": "turnos"})

@app.get("/agenda-view", response_class=HTMLResponse)
def vista_agenda(request: Request):
    return templates.TemplateResponse(request=request, name="agenda.html", context={"active_tab": "agenda"})

@app.get("/clientes-view", response_class=HTMLResponse)
def vista_clientes(request: Request):
    return templates.TemplateResponse(request=request, name="clientes.html", context={"active_tab": "clientes"})

@app.get("/profesionales-view", response_class=HTMLResponse)
def vista_profesionales(request: Request):
    return templates.TemplateResponse(request=request, name="profesionales.html", context={"active_tab": "profesionales"})

@app.get("/servicios-view", response_class=HTMLResponse)
def vista_servicios(request: Request):
    return templates.TemplateResponse(request=request, name="servicios.html", context={"active_tab": "servicios"})

@app.get("/balance-view", response_class=HTMLResponse)
def vista_balance(request: Request):
    return templates.TemplateResponse(request=request, name="balance.html", context={"active_tab": "balance"})


# --- 2. ENDPOINTS REST: TURNOS ---

@app.post("/turnos/")
def agendar_turno(data: TurnoSchema):
    fecha_turno = data.fecha_hora
    if isinstance(fecha_turno, str):
        fecha_turno = datetime.fromisoformat(fecha_turno)

    # Tolerancia de 10 minutos respecto a la hora del servidor
    hace_diez_minutos = datetime.now() - timedelta(minutes=10)
    
    if fecha_turno < hace_diez_minutos:
        raise HTTPException(
            status_code=400, 
            detail="No se pueden agendar turnos con fecha y hora anteriores a la actual."
        )

    try:
        nuevo_turno = Turno(
            id_turno=data.id_turno,
            sucursal_id=data.sucursal_id,
            cliente_id=data.cliente_id,
            profesional_id=data.profesional_id,
            servicio_id=data.servicio_id,
            fecha_hora=fecha_turno,
            detalles_servicio=data.detalles_servicio,
            precio_actual_servicio=data.precio_actual_servicio,
            costo_actual_servicio=data.costo_actual_servicio,
            monto_senia=data.monto_senia,
            metodo_pago=data.metodo_pago,
            estado=data.estado or "En espera"
        )
        turno_creado = agendar_usecase.ejecutar(nuevo_turno)
        return {"mensaje": "Turno agendado exitosamente", "id_turno": turno_creado.id_turno}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/turnos/")
def obtener_turnos(sucursal_id: int):
    """Devuelve todos los turnos persistidos en SQLite para una sucursal."""
    turnos = turno_repo.obtener_por_sucursal(sucursal_id)
    return [
        {
            "id_turno": t.id_turno,
            "sucursal_id": t.sucursal_id,
            "cliente_id": t.cliente_id,
            "profesional_id": t.profesional_id,
            "servicio_id": t.servicio_id,
            "fecha_hora": t.fecha_hora.isoformat(),
            "detalles_servicio": t.detalles_servicio,
            "precio_actual_servicio": t.precio_cobrado,
            "costo_actual_servicio": t.costo_asociado,
            "monto_senia": t.monto_senia,
            "metodo_pago": t.metodo_pago,
            "estado": t.estado
        }
        for t in turnos
    ]

@app.put("/turnos/{id_turno}/estado")
def cambiar_estado_turno(id_turno: int, estado: str):
    """Actualiza el estado de un turno directamente en SQLite."""
    turno = turno_repo.obtener_por_id(id_turno)
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    
    turno.estado = estado
    turno_repo.guardar(turno)
    return {"mensaje": f"Estado actualizado a {estado}"}

@app.delete("/turnos/{id_turno}")
def eliminar_turno(id_turno: int):
    """Elimina un turno de la base de datos SQLite."""
    exito = turno_repo.eliminar_turno(id_turno)
    if not exito:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    return {"mensaje": "Turno eliminado exitosamente"}


# --- 3. ENDPOINTS REST: CLIENTES ---

@app.post("/clientes/")
def crear_cliente(data: ClienteSchema):
    cliente = Cliente(id_cliente=0, nombre=data.nombre, telefono=data.telefono, email=data.email)
    creado = maestros_repo.guardar_cliente(cliente)
    return {"mensaje": "Cliente registrado", "id_cliente": creado.id_cliente}

@app.get("/clientes/")
def listar_clientes():
    return maestros_repo.listar_clientes()

@app.put("/clientes/{id_cliente}")
def modificar_cliente(id_cliente: int, data: ClienteSchema):
    exito = maestros_repo.modificar_cliente(id_cliente, data.nombre, data.telefono, data.email)
    if not exito:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"mensaje": "Cliente modificado correctamente"}

@app.delete("/clientes/{id_cliente}")
def eliminar_cliente(id_cliente: int):
    exito = maestros_repo.eliminar_cliente(id_cliente)
    if not exito:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"mensaje": "Cliente eliminado correctamente"}


# --- 4. ENDPOINTS REST: PROFESIONALES ---

@app.post("/profesionales/")
def crear_profesional(data: ProfesionalSchema):
    profesional = Profesional(id_profesional=0, nombre=data.nombre, especialidad=data.especialidad, sucursal_id=data.sucursal_id)
    creado = maestros_repo.guardar_profesional(profesional)
    return {"mensaje": "Profesional registrado", "id_profesional": creado.id_profesional}

@app.get("/profesionales/")
def listar_profesionales():
    return maestros_repo.listar_profesionales()

@app.put("/profesionales/{id_profesional}")
def modificar_profesional(id_profesional: int, data: ProfesionalSchema):
    exito = maestros_repo.modificar_profesional(id_profesional, data.nombre, data.especialidad, data.sucursal_id)
    if not exito:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    return {"mensaje": "Profesional modificado correctamente"}

@app.delete("/profesionales/{id_profesional}")
def eliminar_profesional(id_profesional: int):
    exito = maestros_repo.eliminar_profesional(id_profesional)
    if not exito:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    return {"mensaje": "Profesional eliminado correctamente"}


# --- 5. ENDPOINTS REST: SERVICIOS ---

@app.post("/servicios/")
def crear_servicio(data: ServicioSchema):
    servicio = Servicio(
        id_servicio=0, 
        nombre=data.nombre, 
        precio_base=data.precio_base, 
        costo_base=data.costo_base,
        duracion_base_minutos=data.duracion_base_minutos or 30
    )
    creado = maestros_repo.guardar_servicio(servicio)
    return {"mensaje": "Servicio registrado correctamente", "id_servicio": creado.id_servicio}

@app.get("/servicios/")
def listar_servicios():
    return maestros_repo.listar_servicios()

@app.put("/servicios/{id_servicio}")
def modificar_servicio(id_servicio: int, data: ServicioSchema):
    exito = maestros_repo.modificar_servicio(
        id_servicio, 
        data.nombre, 
        data.precio_base, 
        data.costo_base,
        data.duracion_base_minutos or 30
    )
    if not exito:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return {"mensaje": "Servicio actualizado correctamente"}

@app.delete("/servicios/{id_servicio}")
def eliminar_servicio(id_servicio: int):
    exito = maestros_repo.eliminar_servicio(id_servicio)
    if not exito:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return {"mensaje": "Servicio eliminado correctamente"}


# --- 6. ENDPOINTS REST: BALANCE Y GASTOS ---

@app.get("/balance/{sucursal_id}")
def obtener_balance(sucursal_id: int):
    return balance_usecase.ejecutar(sucursal_id)

@app.post("/gastos/")
def registrar_gasto(data: GastoSchema):
    try:
        gasto = Gasto(
            id_gasto=0,
            sucursal_id=data.sucursal_id,
            concepto=data.concepto,
            monto=data.monto,
            fecha=datetime.now()
        )
        gasto_repo.registrar_gasto(gasto)
        return {"mensaje": "Gasto registrado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- 7. NOTIFICACIONES WHATSAPP ---

@app.get("/notificaciones/whatsapp/{sucursal_id}")
def obtener_notificaciones_whatsapp(sucursal_id: int, fecha: str, cliente_id: Optional[int] = None):
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
        notificaciones = notificacion_usecase.ejecutar(sucursal_id, fecha_dt)
        
        # Si se especificó cliente_id, filtramos la notificación correspondiente
        if cliente_id:
            notif_cliente = next((n for n in notificaciones if n["cliente_id"] == cliente_id), None)
            if notif_cliente:
                return RedirectResponse(url=notif_cliente["link_whatsapp"])

        if notificaciones:
            return RedirectResponse(url=notificaciones[0]["link_whatsapp"])
        else:
            raise HTTPException(status_code=404, detail="No hay turnos para esa fecha")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usar YYYY-MM-DD")

# --- 8. ENDPOINTS REST: DISPONIBILIDAD DE TURNOS ---

@app.get("/disponibilidad/")
def obtener_disponibilidad(
    sucursal_id: int, 
    fecha: str, 
    duracion_minutos: int, 
    servicio_id: Optional[int] = None,
    profesional_id: Optional[int] = None
):
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
        return disponibilidad_usecase.ejecutar(
            sucursal_id, fecha_dt, duracion_minutos, servicio_id, profesional_id
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usar YYYY-MM-DD")