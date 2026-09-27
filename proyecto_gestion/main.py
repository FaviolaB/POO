
from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info,
    imprimir_advertencia, confirmar, tabla, barra, banner_principal,
    colorear, limpiar_pantalla,
)
from views import ClienteController, EstudianteController


class MenuClientes:
    """VISTA: muestra, pide y presenta. No decide reglas del negocio."""

    TITULO = "SISTEMA DE GESTIÓN DE CLIENTES"
    SUBTITULO = "CRUD completo · Búsqueda · Estadísticas"

    def __init__(self, controlador=ClienteController):
        self._controlador = controlador
        self._activo = True
        self._opciones = self._construir_opciones()

    def _construir_opciones(self):
        return {
            "1": ("Crear", self.crear),
            "2": ("Ver todos", self.listar),
            "3": ("Buscar", self.buscar),
            "4": ("Ver por id", self.ver_por_id),
            "5": ("Actualizar", self.actualizar),
            "6": ("Eliminar", self.eliminar),
            "7": ("Estadísticas", self.estadisticas),
            "8": ("Agrupar por ciudad", self.por_ciudad),
            "0": ("Volver al menú principal", self.salir),
        }

    # ===== ESTÁTICOS: utilidades de pantalla, no dependen del menú =====
    @staticmethod
    def pausa():
        input(colorear("\n  Presione Enter para continuar...", "GRIS"))

    @staticmethod
    def pedir_entero(etiqueta):
        """Devuelve un entero o None si el usuario escribió cualquier otra cosa."""
        try:
            return int(input(colorear(f"  {etiqueta}", "CYAN")))
        except ValueError:
            return None

    @staticmethod
    def mostrar_resultado(exito, mensaje):
        if exito:
            imprimir_exito(mensaje)
        else:
            imprimir_error(mensaje)

    # ===== MÉTODOS DE INSTANCIA =====
    def mostrar_tabla(self, clientes):
        encabezados = ("ID", "NOMBRE", "EMAIL", "CIUDAD", "TELÉFONO")
        filas = [
            (c.id, c.nombre_completo, c.email, c.ciudad or "-", c.telefono or "-")
            for c in clientes
        ]
        tabla(encabezados, filas)
        imprimir_info(f"Total: {len(clientes)} registro(s)")

    def crear(self):
        nombre_modelo = self._controlador.MODELO.__name__
        imprimir_titulo(f"  CREAR {nombre_modelo.upper()}")
        # Recorremos la TUPLA de campos del Modelo: si el Modelo cambia,
        # el formulario cambia solo, sin tocar esta función.
        datos = {}
        for campo in self._controlador.MODELO.CAMPOS:
            datos[campo] = self._pedir_campo_valido(campo)

        exito, mensaje = self._controlador.crear(datos)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def _pedir_campo_valido(self, campo):
        modelo = self._controlador.MODELO
        while True:
            valor = input(colorear(f"  {campo.capitalize()}: ", "CYAN"))
            valor_normalizado, error = modelo.validar_campo(campo, valor)
            if error:
                imprimir_error(error)
                continue
            return valor_normalizado

    def listar(self):
        nombre_modelo = self._controlador.MODELO.__name__
        imprimir_titulo(f"  LISTA DE {nombre_modelo.upper()}S")
        registros = self._controlador.listar()
        if not registros:
            imprimir_info("Todavía no hay registros. Use la opción 1 para crear el primero.")
        else:
            self.mostrar_tabla(registros)
        self.pausa()

    def buscar(self):
        imprimir_titulo("  BUSCAR")
        campos = ", ".join(self._controlador.CAMPOS_BUSCABLES)
        termino = input(colorear(f"  Buscar por ({campos}): ", "CYAN"))
        encontrados = self._controlador.buscar(termino)
        if not encontrados:
            imprimir_info(f"Ningún registro coincide con '{termino}'.")
        else:
            self.mostrar_tabla(encontrados)
        self.pausa()

    def ver_por_id(self):
        imprimir_titulo("  VER POR ID")
        id_registro = self.pedir_entero("Id: ")
        if id_registro is None:
            imprimir_error("El id debe ser un número entero")
            return self.pausa()

        objeto = self._controlador.obtener(id_registro)
        if objeto is None:
            imprimir_error(f"No existe un registro con id {id_registro}")
        else:
            self._mostrar_detalle(objeto)
        self.pausa()

    def _mostrar_detalle(self, objeto):
        print()
        for clave, valor in objeto.a_diccionario().items():
            print(colorear(f"  {clave.capitalize():<12}", "AMARILLO", negrita=True) + f": {valor}")
        if hasattr(objeto, "dominio_email"):
            imprimir_info(f"Dominio del email: {objeto.dominio_email}")

    def actualizar(self):
        imprimir_titulo("  ACTUALIZAR")
        id_registro = self.pedir_entero("Id: ")
        if id_registro is None:
            imprimir_error("El id debe ser un número entero")
            return self.pausa()

        objeto = self._controlador.obtener(id_registro)
        if objeto is None:
            imprimir_error(f"No existe un registro con id {id_registro}")
            return self.pausa()

        imprimir_info(f"Editando a {objeto.nombre_completo}")
        print(colorear("  Deje en blanco el campo que no quiera cambiar.\n", "GRIS"))

        cambios = {}
        for campo in self._controlador.MODELO.CAMPOS:
            actual = getattr(objeto, campo)          # lee la PROPIEDAD
            nuevo = self._pedir_campo_opcional(campo, actual)
            if nuevo is not None:
                cambios[campo] = nuevo

        self.mostrar_resultado(*self._controlador.actualizar(id_registro, cambios))
        self.pausa()

    def _pedir_campo_opcional(self, campo, actual):
        modelo = self._controlador.MODELO
        while True:
            nuevo = input(colorear(f"  {campo.capitalize()} [{actual}]: ", "CYAN")).strip()
            if not nuevo:
                return None
            valor_normalizado, error = modelo.validar_campo(campo, nuevo)
            if error:
                imprimir_error(error)
                continue
            return valor_normalizado

    def eliminar(self):
        imprimir_titulo("  ELIMINAR")
        id_registro = self.pedir_entero("Id: ")
        if id_registro is None:
            imprimir_error("El id debe ser un número entero")
            return self.pausa()

        objeto = self._controlador.obtener(id_registro)
        if objeto is None:
            imprimir_error(f"No existe un registro con id {id_registro}")
            return self.pausa()

        imprimir_advertencia(f"Se eliminará: {objeto}")
        if confirmar("¿Confirma la eliminación?"):
            self.mostrar_resultado(*self._controlador.eliminar(id_registro))
        else:
            imprimir_info("Operación cancelada")
        self.pausa()

    def estadisticas(self):
        imprimir_titulo("  ESTADÍSTICAS")
        datos = self._controlador.estadisticas()
        print(f"  Registrados          : {colorear(str(datos['total']), 'AMARILLO', negrita=True)}")
        print(f"  Ciudades distintas   : {len(datos['ciudades'])} -> {', '.join(datos['ciudades']) or '-'}")
        print(f"  Dominios de email    : {', '.join(datos['dominios']) or '-'}")
        print(f"  Sin teléfono         : {len(datos['sin_telefono'])}")
        self.pausa()

    def por_ciudad(self):
        imprimir_titulo("  AGRUPADOS POR CIUDAD")
        agrupados = self._controlador.agrupar_por_ciudad()
        if not agrupados:
            imprimir_info("Todavía no hay registros.")
        for ciudad, nombres in agrupados.items():
            print(colorear(f"  {ciudad}", "AMARILLO", negrita=True) + f": {', '.join(nombres)}")
        self.pausa()

    def salir(self):
        self._activo = False          # cambia el estado del objeto
        imprimir_info("↩  Volviendo al menú principal...")

    def mostrar_menu(self):
        imprimir_titulo(self.TITULO, self.SUBTITULO)
        for tecla, (texto, _metodo) in self._opciones.items():
            color = "ROJO" if tecla == "0" else "BLANCO"
            print(colorear(f"   {tecla:>2}. {texto}", color))
        print()

    def ejecutar(self):
        """El bucle principal: vive mientras _activo sea True."""
        while self._activo:
            self.mostrar_menu()
            tecla = input(colorear("  Seleccione una opción: ", "VERDE", negrita=True)).strip()

            if tecla not in self._opciones:
                imprimir_error("Opción no válida")
                self.pausa()
                continue

            _texto, metodo = self._opciones[tecla]
            metodo()          # el diccionario guarda el método ya ligado: aquí se ejecuta
        self._activo = True   # se reactiva por si el objeto se vuelve a usar


class MenuEstudiantes(MenuClientes):
    """VISTA: el mismo menú de MenuClientes, apuntando a EstudianteController
    y con las pantallas propias de un estudiante (notas y materias)."""

    TITULO = "SISTEMA DE GESTIÓN DE ESTUDIANTES"
    SUBTITULO = "CRUD · Notas · Promedio · Materias en común"

    def __init__(self, controlador=EstudianteController):
        super().__init__(controlador)

    def _construir_opciones(self):
        opciones = super()._construir_opciones()
        del opciones["8"]      # "Agrupar por ciudad" no aplica a estudiantes
        opciones["8"] = ("Agregar nota", self.agregar_nota)
        opciones["9"] = ("Ver promedio y estado", self.ver_promedio)
        opciones["10"] = ("Materias en común", self.materias_comun)
        opciones["11"] = ("Materias ofertadas", self.materias_ofertadas)
        opciones["0"] = opciones.pop("0")   # reordena: "Salir" queda visualmente al final
        return opciones

    def mostrar_tabla(self, estudiantes):
        encabezados = ("ID", "CARNET", "NOMBRE", "EMAIL", "PROMEDIO", "ESTADO")
        filas = [
            (e.id, e.carnet, e.nombre_completo, e.email, e.promedio, e.estado)
            for e in estudiantes
        ]
        tabla(encabezados, filas)
        imprimir_info(f"Total: {len(estudiantes)} registro(s)")

    def _mostrar_detalle(self, objeto):
        super()._mostrar_detalle(objeto)
        color = "VERDE" if objeto.estado == "Aprobado" else "ROJO"
        imprimir_info(f"Promedio: {objeto.promedio}  ({colorear(objeto.estado, color, negrita=True)})")
        materias = ", ".join(sorted(objeto.materias)) or "sin materias inscritas"
        imprimir_info(f"Materias: {materias}")

    def agregar_nota(self):
        imprimir_titulo("  AGREGAR NOTA")
        id_estudiante = self.pedir_entero("Id del estudiante: ")
        if id_estudiante is None:
            imprimir_error("El id debe ser un número entero")
            return self.pausa()

        objeto = self._controlador.obtener(id_estudiante)
        if objeto is None:
            imprimir_error(f"No existe un estudiante con id {id_estudiante}")
            return self.pausa()

        imprimir_info(f"Estudiante: {objeto.nombre_completo}")
        materia = input(colorear("  Materia: ", "CYAN")).strip()
        try:
            nota = float(input(colorear("  Nota (0 a 20): ", "CYAN")))
        except ValueError:
            imprimir_error("La nota debe ser un número")
            return self.pausa()

        self.mostrar_resultado(*self._controlador.agregar_nota(id_estudiante, materia, nota))
        self.pausa()

    def ver_promedio(self):
        imprimir_titulo("  PROMEDIO Y ESTADO")
        id_estudiante = self.pedir_entero("Id del estudiante: ")
        if id_estudiante is None:
            imprimir_error("El id debe ser un número entero")
            return self.pausa()

        objeto = self._controlador.obtener(id_estudiante)
        if objeto is None:
            imprimir_error(f"No existe un estudiante con id {id_estudiante}")
            return self.pausa()

        color = "VERDE" if objeto.estado == "Aprobado" else "ROJO"
        print()
        print(f"  {colorear(objeto.nombre_completo, 'BLANCO', negrita=True)}")
        print(f"  Promedio : {colorear(str(objeto.promedio), color, negrita=True)} / 20")
        print(f"  Estado   : {colorear(objeto.estado, color, negrita=True)}")
        print(f"  {barra(objeto.promedio, 20, color=color)}  {objeto.promedio}/20\n")
        self.pausa()

    def materias_comun(self):
        imprimir_titulo("  MATERIAS EN COMÚN")
        id_a = self.pedir_entero("Id del primer estudiante: ")
        id_b = self.pedir_entero("Id del segundo estudiante: ")
        if id_a is None or id_b is None:
            imprimir_error("Ambos id deben ser números enteros")
            return self.pausa()

        comunes = self._controlador.materias_en_comun(id_a, id_b)
        if not comunes:
            imprimir_info("No comparten ninguna materia (o algún id no existe).")
        else:
            imprimir_exito(f"Materias en común: {', '.join(sorted(comunes))}")
        self.pausa()

    def materias_ofertadas(self):
        imprimir_titulo("  MATERIAS OFERTADAS")
        materias = self._controlador.materias_ofertadas()
        if not materias:
            imprimir_info("Todavía no hay materias registradas.")
        else:
            for materia in sorted(materias):
                print(colorear(f"  • {materia}", "CYAN"))
        self.pausa()


class MenuPrincipal:
    """VISTA de más alto nivel: decide qué sub-sistema abrir. Tiene estado
    propio (_activo), por eso también es un objeto y no solo métodos de clase."""

    def __init__(self):
        self._activo = True
        self._opciones = {
            "1": ("Gestión de Clientes", lambda: MenuClientes().ejecutar()),
            "2": ("Gestión de Estudiantes", lambda: MenuEstudiantes().ejecutar()),
            "0": ("Salir del programa", self.salir),
        }

    def salir(self):
        self._activo = False
        limpiar_pantalla()
        imprimir_exito("¡Gracias por usar el sistema! Hasta pronto \n")

    def ejecutar(self):
        while self._activo:
            banner_principal()
            for tecla, (texto, _accion) in self._opciones.items():
                color = "ROJO" if tecla == "0" else "BLANCO"
                print(colorear(f"   {tecla}. {texto}", color, negrita=(tecla != "0")))
            print()
            opcion = input(colorear("  Seleccione una opción: ", "VERDE", negrita=True)).strip()

            if opcion not in self._opciones:
                imprimir_error("Opción no válida")
                MenuClientes.pausa()
                continue

            _texto, accion = self._opciones[opcion]
            accion()


if __name__ == "__main__":
    try:
        MenuPrincipal().ejecutar()
    except KeyboardInterrupt:
        print(colorear("\n\n  Programa interrumpido por el usuario.", "GRIS"))