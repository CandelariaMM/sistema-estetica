from datetime import datetime, timedelta, time
from typing import List, Dict, Any

class BuscarDisponibilidadUseCase:

    def __init__(self, turno_repo: Any, maestros_repo: Any):
        self.turno_repo = turno_repo
        self.maestros_repo = maestros_repo

    def ejecutar(
        self, 
        sucursal_id: int, 
        fecha_consulta: datetime.date, 
        duracion_requerida_minutos: int, 
        servicio_id: int = None,
        profesional_id_filtro: int = None
    ) -> List[Dict]:
        
        profesionales = self.maestros_repo.listar_profesionales()
        
        # Filtrar por sucursal
        profs_sucursal = [
            p for p in profesionales 
            if getattr(p, "sucursal_id", 0) == sucursal_id or getattr(p, "sucursal_id", 0) == 0 or getattr(p, "sucursal_id", None) is None
        ]
        if not profs_sucursal:
            profs_sucursal = profesionales

        # Punto 3: Filtrar por profesional específico si se seleccionó en la vista
        if profesional_id_filtro:
            profs_sucursal = [p for p in profs_sucursal if p.id_profesional == profesional_id_filtro]

        turnos_sucursal = self.turno_repo.obtener_por_sucursal(sucursal_id)
        turnos_del_dia = [
            t for t in turnos_sucursal 
            if getattr(t, "fecha_hora", None) and t.fecha_hora.date() == fecha_consulta and getattr(t, "estado", "") != "Cancelado"
        ]

        horario_inicio = time(8, 0)
        horario_fin = time(22, 0)
        
        paso_slot = timedelta(minutes=15)
        duracion_slot = timedelta(minutes=duracion_requerida_minutos)
        ahora = datetime.now()

        sugerencias = []

        for prof in profs_sucursal:
            turnos_prof = [t for t in turnos_del_dia if getattr(t, "profesional_id", None) == prof.id_profesional]
            
            inicio_eval = datetime.combine(fecha_consulta, horario_inicio)
            fin_jornada = datetime.combine(fecha_consulta, horario_fin)

            actual = inicio_eval
            while actual + duracion_slot <= fin_jornada:
                slot_fin = actual + duracion_slot
                
                # Punto 1: Si la fecha es HOY, descartar horarios pasados a la hora actual
                if fecha_consulta == ahora.date() and actual < ahora:
                    actual += paso_slot
                    continue

                ocupado = False
                for t in turnos_prof:
                    duracion_t_min = getattr(t, "duracion_minutos", 30) or 30
                    t_inicio = t.fecha_hora
                    t_fin = t_inicio + timedelta(minutes=duracion_t_min)

                    if max(actual, t_inicio) < min(slot_fin, t_fin):
                        ocupado = True
                        break

                if not ocupado:
                    sugerencias.append({
                        "profesional_id": prof.id_profesional,
                        "profesional_nombre": prof.nombre,
                        "hora_inicio": actual.strftime("%H:%M"),
                        "hora_fin": slot_fin.strftime("%H:%M"),
                        "fecha_hora_iso": actual.strftime("%Y-%m-%dT%H:%M"),
                        "duracion_minutos": duracion_requerida_minutos
                    })
                    actual += duracion_slot
                else:
                    actual += paso_slot

        return sugerencias