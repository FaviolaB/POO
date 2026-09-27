"""
shared/herramientas.py
-----------------------
Utilidades de consola. Son FUNCIONES, no clases: no guardan ningún dato
propio, solo reciben texto y devuelven/imprimen texto. Envolverlas en una
clase no aportaría nada (ver guía, sección 5.5).

Aquí vive también la parte "llamativa" de la interfaz: colores ANSI,
cajas con bordes Unicode y tablas alineadas. Todo con librería estándar,
para que el proyecto corra con un simple `python main.py`, sin instalar
nada extra.
"""
import os
import shutil

# ============================================================
# COLORES (diccionario) y estilos ANSI
# ============================================================
COLORES = {
    "ROJO": "\033[91m",
    "VERDE": "\033[92m",
    "AZUL": "\033[94m",
    "AMARILLO": "\033[93m",
    "CYAN": "\033[96m",
    "MORADO": "\033[95m",
    "BLANCO": "\033[97m",
    "GRIS": "\033[90m",
    "NEGRITA": "\033[1m",
    "RESET": "\033[0m",
}

# TUPLA: respuestas afirmativas aceptadas
RESPUESTAS_SI = ("si", "sí", "s", "yes", "y")

ANCHO_DEFECTO = 78


# ============================================================
# BÁSICOS
# ============================================================
def limpiar_pantalla():
    os.system("clear" if os.name == "posix" else "cls")


def ancho_consola(por_defecto=ANCHO_DEFECTO):
    """Se adapta al ancho real de la terminal si se puede saber."""
    try:
        return max(60, min(shutil.get_terminal_size().columns, 100))
    except OSError:
        return por_defecto


def colorear(texto, color, negrita=False):
    codigo = COLORES.get(color, COLORES["BLANCO"])
    prefijo = COLORES["NEGRITA"] if negrita else ""
    return f"{prefijo}{codigo}{texto}{COLORES['RESET']}"


def imprimir_color(texto, color, negrita=False):
    print(colorear(texto, color, negrita))


def centrar(texto, ancho=None):
    ancho = ancho or ancho_consola()
    return texto.center(ancho)


# ============================================================
# MENSAJES DE ESTADO
# ============================================================
def imprimir_exito(mensaje):
    imprimir_color(f"  ✓ {mensaje}", "VERDE", negrita=True)


def imprimir_error(mensaje):
    imprimir_color(f"  ✗ {mensaje}", "ROJO", negrita=True)


def imprimir_info(mensaje):
    imprimir_color(f"  ℹ {mensaje}", "CYAN")


def imprimir_advertencia(mensaje):
    imprimir_color(f"  ⚠ {mensaje}", "AMARILLO")


def confirmar(pregunta):
    respuesta = input(colorear(f"  {pregunta} (si/no): ", "AMARILLO")).strip().lower()
    return respuesta in RESPUESTAS_SI


# ============================================================
# CAJAS CON BORDES UNICODE
# ============================================================
def caja(lineas, color="AZUL", ancho=None, relleno="═"):
    """Dibuja una caja con bordes Unicode alrededor de una lista de líneas."""
    ancho = ancho or ancho_consola()
    interior = ancho - 2
    borde_sup = "╔" + relleno * interior + "╗"
    borde_inf = "╚" + relleno * interior + "╝"

    salida = [colorear(borde_sup, color)]
    for linea_txt in lineas:
        salida.append(
            colorear("║", color) + linea_txt.center(interior) + colorear("║", color)
        )
    salida.append(colorear(borde_inf, color))
    print("\n".join(salida))


def imprimir_titulo(texto, subtitulo=None):
    """Título de cada pantalla: limpia y dibuja una caja compacta."""
    limpiar_pantalla()
    ancho = ancho_consola()
    interior = ancho - 2
    print(colorear("┌" + "─" * interior + "┐", "AZUL"))
    linea_titulo = colorear(texto, "AMARILLO", negrita=True)
    espacios = interior - len(texto)
    print(colorear("│", "AZUL") + " " * (espacios // 2) + linea_titulo
          + " " * (espacios - espacios // 2) + colorear("│", "AZUL"))
    if subtitulo:
        espacios_s = interior - len(subtitulo)
        linea_sub = colorear(subtitulo, "GRIS")
        print(colorear("│", "AZUL") + " " * (espacios_s // 2) + linea_sub
              + " " * (espacios_s - espacios_s // 2) + colorear("│", "AZUL"))
    print(colorear("└" + "─" * interior + "┘", "AZUL"))
    print()


def banner_principal():
    """Banner grande de bienvenida para el menú principal."""
    limpiar_pantalla()
    ancho = ancho_consola()
    lineas = [
        "",
        "  S I S T E M A   D E   G E S T I Ó N  ",
        "",
        "CRUD  ·  POO  ·  Patrón MVC  ·  Python 3",
        "",
      
    ]
    print(colorear("═" * ancho, "AZUL"))
    print(colorear(lineas[0].center(ancho), "AZUL"))
    print(colorear(lineas[1].center(ancho), "AMARILLO", negrita=True))
    print(colorear(lineas[2].center(ancho), "AZUL"))
    print(colorear(lineas[3].center(ancho), "CYAN"))
    print(colorear(lineas[4].center(ancho), "AZUL"))
    print(colorear("═" * ancho, "AZUL"))
    print()


# ============================================================
# TABLAS ALINEADAS CON BORDES UNICODE
# ============================================================
def tabla(encabezados, filas, anchos=None):
    """
    Imprime una tabla con bordes Unicode.
    encabezados: tupla/lista de textos de columna.
    filas: lista de tuplas/listas con un valor por columna.
    anchos: lista opcional de anchos; si no se da, se calcula del contenido.
    """
    columnas = len(encabezados)
    if anchos is None:
        anchos = []
        for i in range(columnas):
            max_dato = max((len(str(fila[i])) for fila in filas), default=0)
            anchos.append(max(len(str(encabezados[i])), max_dato) + 2)

    def _borde(izq, med, der, relleno="─"):
        return izq + med.join(relleno * a for a in anchos) + der

    print(colorear(_borde("┌", "┬", "┐"), "AZUL"))
    print(colorear("│", "AZUL") +
          colorear("│", "AZUL").join(
              colorear(f" {h}".ljust(a), "AMARILLO", negrita=True) for h, a in zip(encabezados, anchos)
          ) + colorear("│", "AZUL"))
    print(colorear(_borde("├", "┼", "┤"), "AZUL"))
    if not filas:
        interior = sum(anchos) + columnas - 1
        print(colorear("│", "AZUL") + colorear(" Sin registros para mostrar".center(interior), "GRIS")
              + colorear("│", "AZUL"))
    for fila in filas:
        print(colorear("│", "AZUL") +
              colorear("│", "AZUL").join(f" {v}".ljust(a) for v, a in zip(fila, anchos)) +
              colorear("│", "AZUL"))
    print(colorear(_borde("└", "┴", "┘"), "AZUL"))


def barra(valor, maximo, ancho=20, color="VERDE"):
    """Barra de progreso simple, útil para mostrar un promedio visualmente."""
    if maximo <= 0:
        llenos = 0
    else:
        llenos = int(round((valor / maximo) * ancho))
    llenos = max(0, min(ancho, llenos))
    return colorear("█" * llenos, color) + colorear("░" * (ancho - llenos), "GRIS")
