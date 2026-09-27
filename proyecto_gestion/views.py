"""
views.py
--------
CAPA CONTROLADOR (la "C" de MVC, aunque el archivo se llame "views" por
convención histórica de estas guías).

Reglas de esta capa:
    - Las cinco operaciones (Crear, Leer, Buscar, actualizar/Update, Delete).
    - Nunca usa print() ni input(): solo recibe datos y devuelve datos
      (o tuplas (exito, mensaje)).
    - No valida formatos a mano: deja que el Modelo lo haga en sus setters
      y aquí solo atrapa el ValueError.

Todas las operaciones son @classmethod: el Controlador no guarda datos
propios de un objeto, su configuración (qué archivo, qué modelo, qué
campos) vive en la CLASE. Así una subclase (EstudianteController) puede
cambiar esa configuración sin reescribir ni una línea de lógica.
"""
from models import Cliente, Estudiante
from shared.json_manager import GestorJSON


class ClienteController:
    """CONTROLADOR: las cinco operaciones para Cliente. No imprime ni pide datos."""

    # ===== ATRIBUTOS DE CLASE: toda la configuración junta =====
    MODELO = Cliente
    ARCHIVO = "data/clientes.json"
    CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "telefono", "ciudad")
    _gestor = GestorJSON(ARCHIVO)        # se crea una sola vez, al importar el módulo

    # ===== AYUDAS =====
    @classmethod
    def _registros(cls):
        """LISTA de diccionarios, tal como está en el archivo."""
        return cls._gestor.leer()

    @classmethod
    def emails_registrados(cls, excepto_id=None):
        """CONJUNTO de emails ya usados: permite detectar duplicados al instante."""
        return {
            registro["email"].lower()
            for registro in cls._registros()
            if registro["id"] != excepto_id
        }

    @classmethod
    def siguiente_id(cls):
        ids = [registro["id"] for registro in cls._registros()]
        return max(ids) + 1 if ids else 1

    @staticmethod
    def _coincide(registro, termino, campos):
        """Estático: no necesita la clase, solo compara textos."""
        for campo in campos:
            if termino in str(registro.get(campo, "")).lower():
                return True
        return False

    # ===== C · CREATE =====
    @classmethod
    def crear(cls, datos):
        """datos: diccionario. Devuelve la TUPLA (exito, mensaje)."""
        try:
            faltantes = [
                campo for campo in cls.MODELO.OBLIGATORIOS
                if not str(datos.get(campo, "")).strip()
            ]
            if faltantes:
                return False, f"Faltan campos obligatorios: {', '.join(faltantes)}"

            email = str(datos.get("email", "")).strip().lower()
            if email in cls.emails_registrados():
                return False, "Ese email ya está registrado"

            valores = {campo: datos.get(campo, "") for campo in cls.MODELO.CAMPOS}

            # cls.MODELO es la clase: aquí nace el objeto y sus setters validan todo
            objeto = cls.MODELO(cls.siguiente_id(), **valores)

            registros = cls._registros()
            registros.append(objeto.a_diccionario())
            if not cls._gestor.guardar(registros):
                return False, "No se pudo escribir el archivo"

            return True, f"{objeto.nombre_completo} creado con id {objeto.id}"

        except ValueError as error:
            # Los setters del Modelo lanzan ValueError con el mensaje ya listo
            return False, str(error)

    # ===== R · READ =====
    @classmethod
    def listar(cls):
        """LISTA de objetos del Modelo."""
        return [cls.MODELO.desde_diccionario(r) for r in cls._registros()]

    @classmethod
    def obtener(cls, id_registro):
        for objeto in cls.listar():
            if objeto.id == id_registro:
                return objeto
        return None

    # ===== S · SEARCH =====
    @classmethod
    def buscar(cls, termino):
        termino = str(termino).strip().lower()
        if not termino:
            return []
        return [
            cls.MODELO.desde_diccionario(registro)
            for registro in cls._registros()
            if cls._coincide(registro, termino, cls.CAMPOS_BUSCABLES)
        ]

    # ===== U · UPDATE =====
    @classmethod
    def actualizar(cls, id_registro, cambios):
        try:
            # DIFERENCIA DE CONJUNTOS: ¿mandaron campos que no existen?
            desconocidos = set(cambios) - set(cls.MODELO.CAMPOS)
            if desconocidos:
                return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"
            if not cambios:
                return False, "No se indicó ningún cambio"

            objeto = cls.obtener(id_registro)
            if objeto is None:
                return False, f"No existe un registro con id {id_registro}"

            if "email" in cambios:
                nuevo = str(cambios["email"]).strip().lower()
                if nuevo in cls.emails_registrados(excepto_id=id_registro):
                    return False, "Ese email ya lo usa otro registro"

            # setattr le asigna a la PROPIEDAD, así que cada setter valida el valor
            for campo, valor in cambios.items():
                setattr(objeto, campo, valor)

            registros = cls._registros()
            for indice, registro in enumerate(registros):
                if registro["id"] == id_registro:
                    registros[indice] = objeto.a_diccionario()
                    break

            cls._gestor.guardar(registros)
            return True, f"Registro {id_registro} actualizado ({len(cambios)} campo/s)"

        except ValueError as error:
            return False, str(error)

    # ===== D · DELETE =====
    @classmethod
    def eliminar(cls, id_registro):
        registros = cls._registros()
        # Lista nueva sin ese registro: nunca se borra mientras se recorre
        quedan = [r for r in registros if r["id"] != id_registro]

        if len(quedan) == len(registros):
            return False, f"No existe un registro con id {id_registro}"

        cls._gestor.guardar(quedan)
        return True, f"Registro {id_registro} eliminado"

    # ===== EXTRA =====
    @classmethod
    def estadisticas(cls):
        registros = cls._registros()
        ciudades = {r.get("ciudad", "") for r in registros if r.get("ciudad")}
        dominios = {r["email"].split("@")[1] for r in registros if "@" in r["email"]}
        sin_telefono = [r["nombre"] for r in registros if not r.get("telefono")]
        return {
            "total": len(registros),
            "ciudades": sorted(ciudades),
            "dominios": sorted(dominios),
            "sin_telefono": sin_telefono,
        }

    @classmethod
    def agrupar_por_ciudad(cls):
        agrupados = {}
        for objeto in cls.listar():
            ciudad = objeto.ciudad or "Sin ciudad"
            agrupados.setdefault(ciudad, []).append(objeto.nombre_completo)
        return agrupados


class EstudianteController(ClienteController):
    """Hereda las 5 operaciones de ClienteController. Solo cambia la configuración
    y agrega lo que es propio de un estudiante: notas y materias."""

    MODELO = Estudiante
    ARCHIVO = "data/estudiantes.json"
    CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "carnet")
    _gestor = GestorJSON(ARCHIVO)      # cada controlador necesita SU propio gestor

    # --- lo que sí es propio de estudiantes ---
    @classmethod
    def carnets_registrados(cls, excepto_id=None):
        """CONJUNTO de carnets ya usados, igual que emails_registrados() pero
        con el campo 'carnet'."""
        return {
            registro["carnet"].upper()
            for registro in cls._registros()
            if registro["id"] != excepto_id
        }

    @classmethod
    def crear(cls, datos):
        """Repite la validación de duplicados de email (heredada) y agrega
        la de carnet duplicado antes de delegar en el Controlador base."""
        carnet = str(datos.get("carnet", "")).strip().upper()
        if not carnet:
            return False, "Faltan campos obligatorios: carnet"
        if carnet in cls.carnets_registrados():
            return False, "Ese carnet ya está registrado"
        return super().crear(datos)

    @classmethod
    def actualizar(cls, id_registro, cambios):
        """Agrega la validación de carnet duplicado antes de delegar en el
        Controlador base (que ya valida el resto)."""
        if "carnet" in cambios:
            nuevo = str(cambios["carnet"]).strip().upper()
            if nuevo in cls.carnets_registrados(excepto_id=id_registro):
                return False, "Ese carnet ya lo usa otro estudiante"
        return super().actualizar(id_registro, cambios)

    @classmethod
    def agregar_nota(cls, id_estudiante, materia, nota):
        """Obtiene el objeto, llama a objeto.agregar_nota(...), atrapa el
        ValueError del Modelo y, si todo salió bien, vuelve a guardar."""
        objeto = cls.obtener(id_estudiante)
        if objeto is None:
            return False, f"No existe un estudiante con id {id_estudiante}"

        try:
            objeto.agregar_nota(materia, nota)
        except ValueError as error:
            return False, str(error)

        registros = cls._registros()
        for indice, registro in enumerate(registros):
            if registro["id"] == id_estudiante:
                registros[indice] = objeto.a_diccionario()
                break
        cls._gestor.guardar(registros)
        return True, f"Nota {nota} registrada en {materia} para {objeto.nombre_completo}"

    @classmethod
    def materias_ofertadas(cls):
        """Método de clase: CONJUNTO con todas las materias inscritas por
        todos los estudiantes, sin repetir (unión de conjuntos)."""
        todas = set()
        for objeto in cls.listar():
            todas |= objeto.materias
        return todas

    @classmethod
    def materias_en_comun(cls, id_a, id_b):
        """Usa la intersección de conjuntos que ya vive en el Modelo."""
        estudiante_a = cls.obtener(id_a)
        estudiante_b = cls.obtener(id_b)
        if estudiante_a is None or estudiante_b is None:
            return set()
        return estudiante_a.materias_en_comun(estudiante_b)
