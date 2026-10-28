from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.turno import Turno

class TurnoRepository(ABC):

    @abstractmethod
    def guardar(self, turno: Turno) -> Turno:
        """Guarda un nuevo turno o actualiza uno existente."""
        pass

    @abstractmethod
    def obtener_por_id(self, id_turno: int) -> Optional[Turno]:
        """Busca un turno por su ID."""
        pass

    @abstractmethod
    def obtener_por_sucursal(self, sucursal_id: int) -> List[Turno]:
        """Devuelve todos los turnos pertenecientes a una sucursal (Tunuyán o Tupungato)."""
        pass