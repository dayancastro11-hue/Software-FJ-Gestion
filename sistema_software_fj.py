"""
SISTEMA INTEGRAL DE GESTIÓN DE CLIENTES, SERVICIOS Y RESERVAS
Empresa: Software FJ
Curso: Programación - UNAD
Lenguaje: Python 3

El programa no utiliza bases de datos. La información se administra
en objetos y listas durante la ejecución. El archivo software_fj.log
se utiliza únicamente para registrar eventos y errores.
"""

from abc import ABC, abstractmethod
from datetime import datetime
import logging


# ------------------------------------------------------------
# 1. CONFIGURACIÓN DEL ARCHIVO DE REGISTRO (LOGS)
# ------------------------------------------------------------

logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


# ------------------------------------------------------------
# 2. EXCEPCIONES PERSONALIZADAS
# ------------------------------------------------------------

class ErrorSistema(Exception):
    """Excepción general del sistema Software FJ."""


class DatoInvalidoError(ErrorSistema):
    """Se utiliza cuando un dato no cumple las validaciones."""


class ServicioNoDisponibleError(ErrorSistema):
    """Se utiliza cuando un servicio no está disponible."""


class ReservaNoPermitidaError(ErrorSistema):
    """Se utiliza cuando una operación de reserva no está permitida."""


# ------------------------------------------------------------
# 3. CLASE ABSTRACTA ENTIDAD
# ------------------------------------------------------------

class Entidad(ABC):
    def __init__(self, identificador):
        if not identificador or not str(identificador).strip():
            raise DatoInvalidoError("El identificador no puede estar vacío.")
        self._identificador = str(identificador).strip()

    @property
    def identificador(self):
        return self._identificador

    @abstractmethod
    def mostrar_informacion(self):
        pass


# ------------------------------------------------------------
# 4. CLASE CLIENTE
# ------------------------------------------------------------

class Cliente(Entidad):
    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)

        if not nombre or not nombre.strip():
            raise DatoInvalidoError("El nombre del cliente es obligatorio.")

        if not correo or "@" not in correo or "." not in correo:
            raise DatoInvalidoError("El correo electrónico no es válido.")

        if not telefono or not telefono.isdigit() or len(telefono) < 7:
            raise DatoInvalidoError("El teléfono debe tener mínimo 7 dígitos.")

        self.__nombre = nombre.strip()
        self.__correo = correo.strip().lower()
        self.__telefono = telefono.strip()

    @property
    def nombre(self):
        return self.__nombre

    @property
    def correo(self):
        return self.__correo

    @property
    def telefono(self):
        return self.__telefono

    def mostrar_informacion(self):
        return (
            f"Cliente: {self.__nombre} | ID: {self.identificador} | "
            f"Correo: {self.__correo} | Teléfono: {self.__telefono}"
        )


# ------------------------------------------------------------
# 5. CLASE ABSTRACTA SERVICIO
# ------------------------------------------------------------

class Servicio(Entidad, ABC):
    def __init__(self, identificador, nombre, tarifa, disponible=True):
        super().__init__(identificador)

        if not nombre or not nombre.strip():
            raise DatoInvalidoError("El nombre del servicio es obligatorio.")

        if not isinstance(tarifa, (int, float)) or tarifa <= 0:
            raise DatoInvalidoError("La tarifa debe ser un número mayor que cero.")

        self._nombre = nombre.strip()
        self._tarifa = float(tarifa)
        self._disponible = bool(disponible)

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa(self):
        return self._tarifa

    @property
    def disponible(self):
        return self._disponible

    def validar_disponibilidad(self):
        if not self._disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.nombre}' no está disponible."
            )

    # En Python se simula la sobrecarga mediante parámetros opcionales.
    # Se puede llamar calcular_costo(duracion), o calcular_costo(duracion,
    # impuesto=0.19, descuento=0.10).
    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        if not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatoInvalidoError("La duración debe ser mayor que cero.")

        if not 0 <= impuesto <= 1:
            raise DatoInvalidoError("El impuesto debe estar entre 0 y 1.")

        if not 0 <= descuento <= 1:
            raise DatoInvalidoError("El descuento debe estar entre 0 y 1.")

        subtotal = self._tarifa * duracion
        valor_descuento = subtotal * descuento
        base = subtotal - valor_descuento
        total = base + (base * impuesto)
        return round(total, 2)

    @abstractmethod
    def describir_servicio(self):
        pass

    @abstractmethod
    def validar_parametros(self, duracion):
        pass

    @abstractmethod
    def mostrar_informacion(self):
        pass


# ------------------------------------------------------------
# 6. SERVICIOS ESPECIALIZADOS (HERENCIA Y POLIMORFISMO)
# ------------------------------------------------------------

class ReservaSala(Servicio):
    def __init__(self, identificador, nombre, tarifa, capacidad, disponible=True):
        super().__init__(identificador, nombre, tarifa, disponible)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise DatoInvalidoError("La capacidad debe ser un entero positivo.")
        self.capacidad = capacidad

    def validar_parametros(self, duracion):
        self.validar_disponibilidad()
        if duracion < 1:
            raise DatoInvalidoError("La sala debe reservarse por mínimo una hora.")
        return True

    def describir_servicio(self):
        return f"Sala '{self.nombre}' con capacidad para {self.capacidad} personas."

    def mostrar_informacion(self):
        return f"{self.describir_servicio()} Tarifa por hora: ${self.tarifa:,.0f}"


class AlquilerEquipo(Servicio):
    def __init__(self, identificador, nombre, tarifa, cantidad, disponible=True):
        super().__init__(identificador, nombre, tarifa, disponible)
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise DatoInvalidoError("La cantidad de equipos debe ser positiva.")
        self.cantidad = cantidad

    def validar_parametros(self, duracion):
        self.validar_disponibilidad()
        if duracion < 1:
            raise DatoInvalidoError("El alquiler debe ser mínimo de una hora.")
        return True

    def describir_servicio(self):
        return f"Alquiler de {self.nombre}. Unidades disponibles: {self.cantidad}."

    def mostrar_informacion(self):
        return f"{self.describir_servicio()} Tarifa por hora: ${self.tarifa:,.0f}"


class AsesoriaEspecializada(Servicio):
    def __init__(self, identificador, nombre, tarifa, especialidad, disponible=True):
        super().__init__(identificador, nombre, tarifa, disponible)
        if not especialidad or not especialidad.strip():
            raise DatoInvalidoError("Debe indicar la especialidad de la asesoría.")
        self.especialidad = especialidad.strip()

    def validar_parametros(self, duracion):
        self.validar_disponibilidad()
        if duracion < 1:
            raise DatoInvalidoError("La asesoría debe durar mínimo una hora.")
        return True

    def describir_servicio(self):
        return f"Asesoría en {self.especialidad}: {self.nombre}."

    def mostrar_informacion(self):
        return f"{self.describir_servicio()} Tarifa por hora: ${self.tarifa:,.0f}"


# ------------------------------------------------------------
# 7. CLASE RESERVA
# ------------------------------------------------------------

class Reserva(Entidad):
    def __init__(self, identificador, cliente, servicio, duracion):
        super().__init__(identificador)

        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("La reserva debe estar asociada a un cliente.")

        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("La reserva debe tener un servicio válido.")

        servicio.validar_parametros(duracion)

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"
        self.fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def confirmar(self):
        if self.estado != "Pendiente":
            raise ReservaNoPermitidaError(
                "Solo se pueden confirmar reservas pendientes."
            )
        self.servicio.validar_parametros(self.duracion)
        self.estado = "Confirmada"
        logging.info("Reserva %s confirmada.", self.identificador)
        return "La reserva fue confirmada correctamente."

    def cancelar(self):
        if self.estado == "Cancelada":
            raise ReservaNoPermitidaError("La reserva ya está cancelada.")
        if self.estado == "Procesada":
            raise ReservaNoPermitidaError("No se puede cancelar una reserva procesada.")
        self.estado = "Cancelada"
        logging.info("Reserva %s cancelada.", self.identificador)
        return "La reserva fue cancelada."

    def procesar(self, impuesto=0, descuento=0):
        if self.estado != "Confirmada":
            raise ReservaNoPermitidaError(
                "La reserva debe estar confirmada antes de procesarse."
            )

        total = self.servicio.calcular_costo(
            self.duracion, impuesto=impuesto, descuento=descuento
        )
        self.estado = "Procesada"
        logging.info(
            "Reserva %s procesada. Total: $%.2f",
            self.identificador, total
        )
        return total

    def mostrar_informacion(self):
        return (
            f"Reserva: {self.identificador} | Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | Duración: {self.duracion} hora(s) | "
            f"Estado: {self.estado} | Fecha: {self.fecha}"
        )


# ------------------------------------------------------------
# 8. CLASE PRINCIPAL DEL SISTEMA
# ------------------------------------------------------------

class SistemaSoftwareFJ:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("El objeto que intenta registrar no es un cliente.")
        if any(c.identificador == cliente.identificador for c in self.clientes):
            raise DatoInvalidoError("Ya existe un cliente con ese identificador.")
        self.clientes.append(cliente)
        logging.info("Cliente registrado: %s", cliente.identificador)
        return "Cliente registrado correctamente."

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("El objeto que intenta registrar no es un servicio.")
        if any(s.identificador == servicio.identificador for s in self.servicios):
            raise DatoInvalidoError("Ya existe un servicio con ese identificador.")
        self.servicios.append(servicio)
        logging.info("Servicio registrado: %s", servicio.identificador)
        return "Servicio registrado correctamente."

    def registrar_reserva(self, reserva):
        if not isinstance(reserva, Reserva):
            raise DatoInvalidoError("El objeto que intenta registrar no es una reserva.")
        if any(r.identificador == reserva.identificador for r in self.reservas):
            raise DatoInvalidoError("Ya existe una reserva con ese identificador.")
        self.reservas.append(reserva)
        logging.info("Reserva creada: %s", reserva.identificador)
        return "Reserva creada correctamente."

    def listar_clientes(self):
        for cliente in self.clientes:
            print(cliente.mostrar_informacion())

    def listar_servicios(self):
        for servicio in self.servicios:
            print(servicio.mostrar_informacion())

    def listar_reservas(self):
        for reserva in self.reservas:
            print(reserva.mostrar_informacion())


# ------------------------------------------------------------
# 9. FUNCIÓN PARA EJECUTAR OPERACIONES SIN DETENER EL SISTEMA
# ------------------------------------------------------------

def ejecutar_operacion(descripcion, funcion):
    print(f"\n--- {descripcion} ---")
    try:
        resultado = funcion()
    except ErrorSistema as error:
        logging.error("%s: %s", descripcion, error)
        print(f"Error controlado: {error}")
    except Exception as error:
        # Encadenamiento: se registra la excepción original y se genera
        # una excepción del sistema conservando su causa.
        logging.exception("Error inesperado durante: %s", descripcion)
        try:
            raise ErrorSistema("Ocurrió un error inesperado en la operación.") from error
        except ErrorSistema as error_encadenado:
            print(f"Error inesperado controlado: {error_encadenado}")
            print(f"Causa original: {error_encadenado.__cause__}")
    else:
        print(resultado)
        logging.info("Operación exitosa: %s", descripcion)
    finally:
        print("Operación finalizada. El sistema continúa activo.")


# ------------------------------------------------------------
# 10. PRUEBAS: MÁS DE 10 OPERACIONES COMPLETAS
# ------------------------------------------------------------

def main():
    sistema = SistemaSoftwareFJ()

    print("=" * 65)
    print("       SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ")
    print("=" * 65)

    # Operación 1: registro correcto de cliente.
    cliente1 = Cliente("C001", "Carlos Pérez", "carlos@gmail.com", "3001234567")
    ejecutar_operacion(
        "1. Registrar cliente válido",
        lambda: sistema.registrar_cliente(cliente1)
    )

    # Operación 2: registro de otro cliente.
    cliente2 = Cliente("C002", "Laura Gómez", "laura@gmail.com", "3107654321")
    ejecutar_operacion(
        "2. Registrar segundo cliente",
        lambda: sistema.registrar_cliente(cliente2)
    )

    # Operación 3: intentar crear cliente con correo inválido.
    def cliente_invalido():
        cliente = Cliente("C003", "Pedro Díaz", "correo_invalido", "3005556677")
        return sistema.registrar_cliente(cliente)

    ejecutar_operacion("3. Registrar cliente con correo inválido", cliente_invalido)

    # Operación 4: crear y registrar servicio de sala.
    sala = ReservaSala("S001", "Sala de reuniones", 50000, 20)
    ejecutar_operacion(
        "4. Registrar servicio de reserva de sala",
        lambda: sistema.registrar_servicio(sala)
    )

    # Operación 5: crear y registrar alquiler de equipos.
    equipo = AlquilerEquipo("S002", "Video beam", 30000, 5)
    ejecutar_operacion(
        "5. Registrar servicio de alquiler de equipos",
        lambda: sistema.registrar_servicio(equipo)
    )

    # Operación 6: crear y registrar asesoría.
    asesoria = AsesoriaEspecializada(
        "S003", "Asesoría tecnológica", 80000, "Tecnología"
    )
    ejecutar_operacion(
        "6. Registrar servicio de asesoría especializada",
        lambda: sistema.registrar_servicio(asesoria)
    )

    # Operación 7: intentar crear servicio con tarifa inválida.
    def servicio_invalido():
        servicio = ReservaSala("S004", "Sala inválida", -1000, 10)
        return sistema.registrar_servicio(servicio)

    ejecutar_operacion("7. Crear servicio con tarifa inválida", servicio_invalido)

    # Operación 8: crear y registrar reserva válida.
    reserva1 = Reserva("R001", cliente1, sala, 2)
    ejecutar_operacion(
        "8. Crear reserva válida",
        lambda: sistema.registrar_reserva(reserva1)
    )

    # Operación 9: confirmar reserva.
    ejecutar_operacion("9. Confirmar reserva", reserva1.confirmar)

    # Operación 10: procesar reserva con impuesto del 19%.
    ejecutar_operacion(
        "10. Procesar reserva con impuesto",
        lambda: f"Total a pagar: ${reserva1.procesar(impuesto=0.19):,.2f}"
    )

    # Operación 11: intentar procesar una reserva que no está confirmada.
    reserva2 = Reserva("R002", cliente2, equipo, 3)
    ejecutar_operacion(
        "11. Crear segunda reserva",
        lambda: sistema.registrar_reserva(reserva2)
    )
    ejecutar_operacion(
        "12. Intentar procesar reserva pendiente",
        lambda: reserva2.procesar()
    )

    # Operación 13: cancelar reserva pendiente.
    ejecutar_operacion("13. Cancelar segunda reserva", reserva2.cancelar)

    # Operación 14: intentar reservar un servicio no disponible.
    def servicio_no_disponible():
        servicio = AsesoriaEspecializada(
            "S005", "Asesoría temporal", 60000, "Sistemas", disponible=False
        )
        sistema.registrar_servicio(servicio)
        return Reserva("R003", cliente1, servicio, 1)

    ejecutar_operacion(
        "14. Intentar reservar un servicio no disponible",
        servicio_no_disponible
    )

    # Operación 15: demostrar cálculo con descuento e impuesto.
    ejecutar_operacion(
        "15. Calcular costo con descuento e impuesto",
        lambda: (
            f"Costo final de 2 horas de asesoría: "
            f"${asesoria.calcular_costo(2, impuesto=0.19, descuento=0.10):,.2f}"
        )
    )

    print("\n" + "=" * 65)
    print("RESUMEN FINAL DEL SISTEMA")
    print("=" * 65)
    print(f"Clientes registrados: {len(sistema.clientes)}")
    print(f"Servicios registrados: {len(sistema.servicios)}")
    print(f"Reservas registradas: {len(sistema.reservas)}")

    print("\nLISTADO DE CLIENTES")
    sistema.listar_clientes()

    print("\nLISTADO DE SERVICIOS")
    sistema.listar_servicios()

    print("\nLISTADO DE RESERVAS")
    sistema.listar_reservas()

    print("\nEl archivo 'software_fj.log' contiene el registro de eventos y errores.")
    print("Fin de la ejecución.")


if __name__ == "__main__":
    main()
