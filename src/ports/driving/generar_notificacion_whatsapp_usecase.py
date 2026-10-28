import urllib.parse
from datetime import datetime
from typing import List, Dict
from src.ports.driven.turno_repository import TurnoRepository

class GenerarNotificacionWhatsAppUseCase:

    def __init__(self, turno_repo: TurnoRepository, maestros_repo=None):
        self.turno_repo = turno_repo
        self.maestros_repo = maestros_repo

    def ejecutar(self, sucursal_id: int, fecha: datetime) -> List[Dict[str, str]]:
        turnos = self.turno_repo.obtener_por_sucursal(sucursal_id)
        
        # Obtener mapa de clientes si el repositorio maestro está disponible
        clientes_map = {}
        if self.maestros_repo:
            try:
                clientes = self.maestros_repo.listar_clientes()
                clientes_map = {c.id_cliente: c for c in clientes}
            except Exception:
                pass

        notificaciones = []

        for turno in turnos:
            if turno.fecha_hora.date() == fecha.date() and turno.estado != "Cancelado":
                # Soporte seguro para el atributo de precio
                precio = getattr(turno, "precio_cobrado", getattr(turno, "precio_actual_servicio", 0.0))
                monto_senia = getattr(turno, "monto_senia", 0.0)
                monto_pendiente = precio - monto_senia
                
                hora_str = turno.fecha_hora.strftime("%H:%M")

                cliente = clientes_map.get(turno.cliente_id)
                nombre_cliente = cliente.nombre if cliente else "Estimada clienta"
                telefono_cliente = cliente.telefono if cliente else ""

                # Limpieza del teléfono para el formato wa.me/549...
                telefono_limpio = "".join(filter(str.isdigit, telefono_cliente))
                if telefono_limpio and not telefono_limpio.startswith("549"):
                    if telefono_limpio.startswith("15"):
                        telefono_limpio = telefono_limpio[2:]
                    if not telefono_limpio.startswith("54"):
                        telefono_limpio = "549" + telefono_limpio

                # Mensaje personalizado
                mensaje = (
                    f"Hola {nombre_cliente}! Te recordamos tu turno para {turno.detalles_servicio} "
                    f"el día {turno.fecha_hora.strftime('%d/%m')} a las {hora_str} hs. "
                )
                
                if monto_pendiente > 0:
                    mensaje += f"Saldo pendiente: ${monto_pendiente:.0f}. "
                
                mensaje += "¡Te esperamos en la estética!"

                mensaje_encoded = urllib.parse.quote(mensaje)
                
                # Link directo al chat de WhatsApp del cliente
                if telefono_limpio:
                    link_wa = f"https://wa.me/{telefono_limpio}?text={mensaje_encoded}"
                else:
                    link_wa = f"https://wa.me/?text={mensaje_encoded}"

                notificaciones.append({
                    "id_turno": turno.id_turno,
                    "cliente_id": turno.cliente_id,
                    "detalles_servicio": turno.detalles_servicio,
                    "hora": hora_str,
                    "mensaje": mensaje,
                    "link_whatsapp": link_wa
                })

        return notificaciones