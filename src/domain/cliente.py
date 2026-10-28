class Cliente:
    def __init__(self, id_cliente: int, nombre: str, telefono: str, email: str = ""):
        if not nombre.strip():
            raise ValueError("El nombre del cliente no puede estar vacío")
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.telefono = telefono
        self.email = email