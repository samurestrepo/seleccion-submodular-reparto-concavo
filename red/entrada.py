"""Lectura de una instancia desde un archivo JSON (formato provisional, informe 6.5).

Es el ÚNICO archivo que conoce el formato de entrada. Si llegan los casos de la
profesora con otro formato, solo se cambia este archivo.

Revisa la FORMA del archivo (campos, tipos y que los números de las utilidades sirvan).
Las restricciones del problema (k < N, concavidad, etc.) las revisa verificacion.py
y quedan en la traza. Cualquier problema de forma se reporta como ErrorDeFormato.
"""

import json

from red.utilidades import crear_utilidad


class ErrorDeFormato(Exception):
    """El archivo no tiene la forma esperada."""


class Nodo:
    """Un nodo candidato: su identificador, lo que cubre (Parte 2) y su utilidad (Parte 1)."""

    def __init__(self, id, cubre, utilidad):
        self.id = id
        self.cubre = frozenset(cubre)
        self.utilidad = utilidad


class Instancia:
    """Un caso completo: k, B y la lista de nodos ordenada por id."""

    def __init__(self, k, B, nodos, nombre="sin_nombre"):
        self.k = k
        self.B = B
        self.nodos = sorted(nodos, key=lambda nodo: nodo.id)
        self.nombre = nombre

    @property
    def N(self):
        """Número de nodos candidatos."""
        return len(self.nodos)

    def ids(self):
        """Identificadores en orden creciente (el orden en que el voraz recorre V)."""
        return [nodo.id for nodo in self.nodos]

    def conjuntos(self):
        """Diccionario id → conjunto que cubre (para el oráculo de la Parte 2)."""
        return {nodo.id: nodo.cubre for nodo in self.nodos}

    def utilidades(self):
        """Diccionario id → función de utilidad (para la Parte 1)."""
        return {nodo.id: nodo.utilidad for nodo in self.nodos}


def _exigir_entero(valor, campo):
    """Devuelve valor si es un entero. Un bool no cuenta. Si no, lanza ErrorDeFormato."""
    if not isinstance(valor, int) or isinstance(valor, bool):
        raise ErrorDeFormato(f"'{campo}' debe ser un entero; llegó {valor!r}")
    return valor


def _leer_nodo(d, posicion):
    """Convierte el objeto JSON de un nodo en un Nodo. Lanza ErrorDeFormato si no cuadra.

    Recibe el objeto y su posición en la lista (para el mensaje de error).
    Tiempo O(|cubre| + L), con L el largo de la tabla de ganancias (0 en log y raíz).
    """
    if not isinstance(d, dict):
        raise ErrorDeFormato(f"el nodo en la posición {posicion} debe ser un objeto; llegó {d!r}")
    for campo in ("id", "cubre", "utilidad"):
        if campo not in d:
            raise ErrorDeFormato(f"al nodo en la posición {posicion} le falta '{campo}'")
    id_nodo = _exigir_entero(d["id"], f"nodos[{posicion}].id")
    if not isinstance(d["cubre"], list):
        raise ErrorDeFormato(f"'cubre' del nodo {id_nodo} debe ser una lista")
    if not isinstance(d["utilidad"], dict):
        raise ErrorDeFormato(f"'utilidad' del nodo {id_nodo} debe ser un objeto; llegó {d['utilidad']!r}")
    try:
        utilidad = crear_utilidad(d["utilidad"])
    except KeyError as error:
        raise ErrorDeFormato(f"utilidad del nodo {id_nodo}: falta el campo {error}") from error
    except (ValueError, TypeError) as error:
        raise ErrorDeFormato(f"utilidad del nodo {id_nodo}: {error}") from error
    try:
        return Nodo(id_nodo, d["cubre"], utilidad)
    except TypeError as error:   # frozenset no acepta listas ni objetos como elementos
        raise ErrorDeFormato(f"'cubre' del nodo {id_nodo} no puede tener listas ni objetos") from error


def instancia_desde_diccionario(datos, nombre="sin_nombre"):
    """Convierte el contenido leído del JSON en una Instancia.

    Recibe: {"k": int, "B": int, "nodos": [{"id", "cubre", "utilidad"}, ...]}.
    Devuelve: Instancia. Lanza ErrorDeFormato si falta un campo o un tipo no cuadra.
    Tiempo O(N + M + ΣL), con M = total de elementos en "cubre" y L = largo de cada tabla.
    """
    if not isinstance(datos, dict):
        raise ErrorDeFormato(f"el archivo debe ser un objeto con k, B y nodos; llegó {datos!r}")
    for campo in ("k", "B", "nodos"):
        if campo not in datos:
            raise ErrorDeFormato(f"falta el campo '{campo}'")
    k = _exigir_entero(datos["k"], "k")
    B = _exigir_entero(datos["B"], "B")
    if not isinstance(datos["nodos"], list):
        raise ErrorDeFormato("'nodos' debe ser una lista")

    nodos = [_leer_nodo(d, posicion) for posicion, d in enumerate(datos["nodos"])]
    return Instancia(k, B, nodos, nombre)


def nombre_del_caso(ruta):
    """El nombre de un caso: el del archivo, sin la extensión .json (en mayúsculas o minúsculas)."""
    nombre = str(ruta).replace("\\", "/").split("/")[-1]
    if nombre.lower().endswith(".json"):
        nombre = nombre[:-len(".json")]
    return nombre


def leer_instancia(ruta):
    """Lee un archivo JSON y devuelve la Instancia. El nombre del caso es el del archivo.

    Acepta UTF-8 con o sin BOM (el BOM es la marca invisible que agregan algunos editores
    de Windows). Lanza ErrorDeFormato si no es UTF-8 o no es JSON; OSError si no se puede abrir.
    """
    with open(ruta, encoding="utf-8-sig") as archivo:
        try:
            datos = json.load(archivo)
        except UnicodeDecodeError as error:
            raise ErrorDeFormato(f"{ruta} no está codificado en UTF-8: {error}") from error
        except (ValueError, RecursionError) as error:   # ValueError incluye json.JSONDecodeError
            raise ErrorDeFormato(f"{ruta} no es un JSON válido: {error}") from error
    return instancia_desde_diccionario(datos, nombre_del_caso(ruta))
