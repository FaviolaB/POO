"""
models.py
---------
CAPA MODELO (la "M" de MVC).

Reglas de esta capa:
    - Define qué ES un Cliente y qué ES un Estudiante, y las reglas que
      un dato válido debe cumplir.
    - Los objetos se defienden solos: si un dato está mal, el objeto
      NO llega a existir (el constructor lanza ValueError).
    - Nunca lee archivos, nunca usa input() ni print(). No sabe que
      existe una consola ni un archivo JSON.

Inventario de POO en este archivo:
    - Atributos de clase ("estáticos"): CAMPOS, OBLIGATORIOS, total_creados...
    - Atributos privados: __id, __nombre, __email... (name mangling de Python)
    - Propiedades: de lectura/escritura (nombre), de solo lectura (id)
      y calculadas (nombre_completo, promedio, estado).
    - @classmethod: desde_diccionario(), fábricas de objetos.
    - @staticmethod: limpiar(), es_email_valido(), es_telefono_valido()...
"""


class Cliente:
    """MODELO: un cliente válido. Si los datos están mal, el objeto no se crea."""

    # ===== ATRIBUTOS DE CLASE (estáticos): existen una sola vez =====
    CAMPOS = ("nombre", "apellido", "email", "telefono", "ciudad", "direccion")
    OBLIGATORIOS = ("nombre", "apellido", "email")
    total_creados = 0

    def __init__(self, id_cliente, nombre, apellido, email,
                 telefono="", ciudad="", direccion=""):
        self.__id = id_cliente        # privado y sin setter: no se puede cambiar
        # Asignamos por las PROPIEDADES para que la validación corra también al crear
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.telefono = telefono
        self.ciudad = ciudad
        self.direccion = direccion
        Cliente.total_creados += 1    # el contador vive en la CLASE, no en el objeto

    # ===== MÉTODOS ESTÁTICOS: reglas que no dependen de ningún cliente =====
    @staticmethod
    def limpiar(texto):
        return str(texto).strip()

    @staticmethod
    def es_email_valido(texto):
        texto = str(texto).strip()
        if texto.count("@") != 1:
            return False
        usuario, dominio = texto.split("@")
        return len(usuario) > 0 and "." in dominio and not dominio.endswith(".")

    @staticmethod
    def es_nombre_valido(texto):
        # Válido si tiene al menos una letra y NO contiene números ni símbolos.
        # isalpha() también acepta tildes y ñ, así que "José" sigue siendo válido.
        texto = str(texto).strip()
        return texto != "" and all(c.isalpha() or c.isspace() for c in texto)

    @staticmethod
    def es_telefono_valido(texto):
        # Válido si está vacío (es opcional) o si son exactamente 10 dígitos
        texto = str(texto).strip()
        return texto == "" or (texto.isdigit() and len(texto) == 10)

    # ===== PROPIEDADES =====
    @property
    def id(self):
        # SOLO LECTURA: no tiene setter, así que cliente.id = 5 lanza AttributeError
        return self.__id

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        valor = Cliente.limpiar(valor)
        if not valor:
            raise ValueError("El nombre es obligatorio")
        if not Cliente.es_nombre_valido(valor):
            raise ValueError("El nombre solo puede contener letras (sin números)")
        self.__nombre = valor.title()

    @property
    def apellido(self):
        return self.__apellido

    @apellido.setter
    def apellido(self, valor):
        valor = Cliente.limpiar(valor)
        if not valor:
            raise ValueError("El apellido es obligatorio")
        if not Cliente.es_nombre_valido(valor):
            raise ValueError("El apellido solo puede contener letras (sin números)")
        self.__apellido = valor.title()

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, valor):
        valor = Cliente.limpiar(valor)
        if not Cliente.es_email_valido(valor):
            raise ValueError(f"Email inválido: '{valor}'")
        self.__email = valor.lower()

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        valor = Cliente.limpiar(valor)
        if not Cliente.es_telefono_valido(valor):
            raise ValueError("El teléfono debe estar vacío o tener exactamente 10 dígitos")
        self.__telefono = valor

    @property
    def ciudad(self):
        return self.__ciudad

    @ciudad.setter
    def ciudad(self, valor):
        self.__ciudad = Cliente.limpiar(valor).title()

    @property
    def direccion(self):
        return self.__direccion

    @direccion.setter
    def direccion(self, valor):
        self.__direccion = Cliente.limpiar(valor)

    # PROPIEDADES CALCULADAS: no guardan nada, se calculan al leerlas
    @property
    def nombre_completo(self):
        return f"{self.__nombre} {self.__apellido}"

    @property
    def iniciales(self):
        return f"{self.__nombre[0]}.{self.__apellido[0]}.".upper()

    @property
    def dominio_email(self):
        return self.__email.split("@")[1]

    # ===== MÉTODOS DE INSTANCIA: necesitan los datos de ESTE cliente =====
    def a_diccionario(self):
        return {
            "id": self.__id,
            "nombre": self.__nombre,
            "apellido": self.__apellido,
            "email": self.__email,
            "telefono": self.__telefono,
            "ciudad": self.__ciudad,
            "direccion": self.__direccion,
        }

    def __str__(self):
        return f"[{self.__id}] {self.nombre_completo} - {self.__email}"

    # ===== MÉTODOS DE CLASE =====
    @classmethod
    def desde_diccionario(cls, datos):
        # cls es la clase: si mañana existe ClienteVIP(Cliente),
        # ClienteVIP.desde_diccionario(d) devolverá un ClienteVIP.
        return cls(
            datos["id"],
            datos["nombre"],
            datos["apellido"],
            datos["email"],
            datos.get("telefono", ""),
            datos.get("ciudad", ""),
            datos.get("direccion", ""),
        )

    @classmethod
    def resumen(cls):
        return f"Se han creado {cls.total_creados} clientes en esta ejecución"

    @classmethod
    def validar_campo(cls, campo, valor):
        """Valida y normaliza UN solo campo, sin crear el objeto completo.
        Devuelve (valor_normalizado, None) si es válido, o (None, mensaje)
        si no lo es. Usa las mismas reglas que los setters de arriba, para
        que la Vista pueda preguntar de nuevo campo por campo ANTES de
        intentar crear el objeto."""
        valor = cls.limpiar(valor)

        if campo in ("nombre", "apellido"):
            etiqueta = "nombre" if campo == "nombre" else "apellido"
            if not valor:
                return None, f"El {etiqueta} es obligatorio"
            if not cls.es_nombre_valido(valor):
                return None, f"El {etiqueta} solo puede contener letras (sin números)"
            return valor.title(), None

        if campo == "email":
            if not valor:
                return None, "El email es obligatorio"
            if not cls.es_email_valido(valor):
                return None, f"Email inválido: '{valor}'"
            return valor.lower(), None

        if campo == "telefono":
            if not cls.es_telefono_valido(valor):
                return None, "El teléfono debe estar vacío o tener exactamente 10 dígitos"
            return valor, None

        if campo == "ciudad":
            return valor.title(), None

        if campo == "direccion":
            return valor, None

        return valor, None


class Estudiante:
    """MODELO: un estudiante con sus materias (set) y sus notas (dict de listas)."""

    CAMPOS = ("nombre", "apellido", "email", "carnet")
    OBLIGATORIOS = ("nombre", "apellido", "email", "carnet")
    NOTA_MINIMA = 0
    NOTA_MAXIMA = 20
    NOTA_APROBACION = 14
    total_creados = 0

    def __init__(self, id_estudiante, nombre, apellido, email, carnet,
                 notas=None, materias=None):
        self.__id = id_estudiante
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.carnet = carnet
        self.__notas = dict(notas) if notas else {}              # DICCIONARIO de LISTAS
        self.__materias = set(materias) if materias else set()   # CONJUNTO
        Estudiante.total_creados += 1

    # ===== ESTÁTICOS =====
    @staticmethod
    def limpiar(texto):
        return str(texto).strip()

    @staticmethod
    def es_nota_valida(nota):
        # No usa self ni cls: es una regla suelta, por eso es estático
        return isinstance(nota, (int, float)) and \
            Estudiante.NOTA_MINIMA <= nota <= Estudiante.NOTA_MAXIMA

    @staticmethod
    def es_nombre_valido(texto):
        texto = str(texto).strip()
        return texto != "" and all(c.isalpha() or c.isspace() for c in texto)

    # ===== PROPIEDADES =====
    @property
    def id(self):
        return self.__id

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        valor = Estudiante.limpiar(valor)
        if not valor:
            raise ValueError("El nombre es obligatorio")
        if not Estudiante.es_nombre_valido(valor):
            raise ValueError("El nombre solo puede contener letras (sin números)")
        self.__nombre = valor.title()

    @property
    def apellido(self):
        return self.__apellido

    @apellido.setter
    def apellido(self, valor):
        valor = Estudiante.limpiar(valor)
        if not valor:
            raise ValueError("El apellido es obligatorio")
        if not Estudiante.es_nombre_valido(valor):
            raise ValueError("El apellido solo puede contener letras (sin números)")
        self.__apellido = valor.title()

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, valor):
        valor = Estudiante.limpiar(valor)
        if "@" not in valor:
            raise ValueError(f"Email inválido: '{valor}'")
        self.__email = valor.lower()

    @property
    def carnet(self):
        return self.__carnet

    @carnet.setter
    def carnet(self, valor):
        valor = Estudiante.limpiar(valor).upper()
        if len(valor) < 4:
            raise ValueError("El carnet debe tener al menos 4 caracteres")
        self.__carnet = valor

    @property
    def materias(self):
        # Devolvemos una COPIA: así nadie modifica el conjunto interno desde afuera
        return set(self.__materias)

    @property
    def nombre_completo(self):
        return f"{self.__nombre} {self.__apellido}"

    @property
    def promedio(self):
        # CALCULADA: recorre el diccionario de listas cada vez que se lee
        todas = []
        for lista_notas in self.__notas.values():
            todas.extend(lista_notas)
        return round(sum(todas) / len(todas), 2) if todas else 0

    @property
    def estado(self):
        # CALCULADA: si todavía no tiene ninguna nota, no es justo decir
        # "Reprobado" (suena a que ya falló). Solo evaluamos Aprobado/
        # Reprobado cuando ya existe al menos una nota registrada.
        if not self.__notas:
            return "Pendiente"
        return "Aprobado" if self.promedio >= Estudiante.NOTA_APROBACION else "Reprobado"

    # ===== MÉTODOS DE INSTANCIA =====
    def inscribir_materia(self, materia):
        materia = Estudiante.limpiar(materia).title()
        if not materia:
            raise ValueError("La materia no puede estar vacía")
        self.__materias.add(materia)        # add() no duplica
        return materia

    def agregar_nota(self, materia, nota):
        if not Estudiante.es_nota_valida(nota):
            raise ValueError(
                f"La nota debe estar entre {Estudiante.NOTA_MINIMA} y {Estudiante.NOTA_MAXIMA}"
            )
        materia = self.inscribir_materia(materia)
        self.__notas.setdefault(materia, []).append(nota)

    def notas_de(self, materia):
        return list(self.__notas.get(Estudiante.limpiar(materia).title(), []))

    def materias_en_comun(self, otro):
        # INTERSECCIÓN de conjuntos
        return self.__materias & otro.materias

    def a_diccionario(self):
        return {
            "id": self.__id,
            "nombre": self.__nombre,
            "apellido": self.__apellido,
            "email": self.__email,
            "carnet": self.__carnet,
            "notas": self.__notas,
            "materias": sorted(self.__materias),   # JSON no guarda sets
        }

    def __str__(self):
        return f"[{self.__carnet}] {self.nombre_completo} - Promedio: {self.promedio} ({self.estado})"

    # ===== MÉTODO DE CLASE =====
    @classmethod
    def desde_diccionario(cls, datos):
        return cls(
            datos["id"], datos["nombre"], datos["apellido"], datos["email"],
            datos["carnet"],
            notas=datos.get("notas", {}),
            materias=set(datos.get("materias", [])),   # lista -> conjunto otra vez
        )

    @classmethod
    def resumen(cls):
        return f"Se han creado {cls.total_creados} estudiantes en esta ejecución"

    @classmethod
    def validar_campo(cls, campo, valor):
        """Igual que en Cliente: valida y normaliza UN solo campo, sin crear
        el objeto completo, para que la Vista pueda preguntar de nuevo."""
        valor = cls.limpiar(valor)

        if campo in ("nombre", "apellido"):
            etiqueta = "nombre" if campo == "nombre" else "apellido"
            if not valor:
                return None, f"El {etiqueta} es obligatorio"
            if not cls.es_nombre_valido(valor):
                return None, f"El {etiqueta} solo puede contener letras (sin números)"
            return valor.title(), None

        if campo == "email":
            if not valor:
                return None, "El email es obligatorio"
            if "@" not in valor:
                return None, f"Email inválido: '{valor}'"
            return valor.lower(), None

        if campo == "carnet":
            if not valor:
                return None, "El carnet es obligatorio"
            if len(valor) < 4:
                return None, "El carnet debe tener al menos 4 caracteres"
            return valor.upper(), None

        return valor, None