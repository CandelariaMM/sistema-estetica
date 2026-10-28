from abc import ABC, abstractmethod
from typing import List
from src.domain.gasto import Gasto

class GastoRepository(ABC):

    @abstractmethod
    def registrar_gasto(self, gasto: Gasto) -> Gasto:
        pass

    @abstractmethod
    def obtener_por_sucursal(self, sucursal_id: int) -> List[Gasto]:
        pass