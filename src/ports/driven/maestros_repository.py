from abc import ABC, abstractmethod
from typing import List
from src.domain.cliente import Cliente
from src.domain.profesional import Profesional
from src.domain.servicio import Servicio

class MaestrosRepository(ABC):

    # --- CLIENTES ---
    @abstractmethod
    def guardar_cliente(self, cliente: Cliente) -> Cliente:
        pass

    @abstractmethod
    def listar_clientes(self) -> List[Cliente]:
        pass

    # --- PROFESIONALES ---
    @abstractmethod
    def guardar_profesional(self, profesional: Profesional) -> Profesional:
        pass

    @abstractmethod
    def listar_profesionales(self) -> List[Profesional]:
        pass

    # --- SERVICIOS ---
    @abstractmethod
    def guardar_servicio(self, servicio: Servicio) -> Servicio:
        pass

    @abstractmethod
    def listar_servicios(self) -> List[Servicio]:
        pass