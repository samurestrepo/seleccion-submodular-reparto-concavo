"""Lectura de una instancia desde un archivo JSON (formato provisional, informe 6.5).

Es el ÚNICO archivo que conoce el formato de entrada. Si llegan los casos de la
profesora con otro formato, solo se cambia este archivo.

Revisa la FORMA del archivo (campos, tipos). Las restricciones del problema
(k < N, concavidad, etc.) las revisa verificacion.py y quedan en la traza.
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
    if not isinstance(valor, int) or isinstance(valor, bool):
        raise ErrorDeFormato(f"'{campo}' debe ser un entero; llegó {valor!r}")
    return valor


def instancia_desde_diccionario(datos, nombre="sin_nombre"):
    """Convierte el diccionario leído del JSON en una Instancia.

    Recibe: {"k": int, "B": int, "nodos": [{"id", "cubre", "utilidad"}, ...]}.
    Devuelve: Instancia. Lanza ErrorDeFormato si falta un campo o un tipo no cuadra.
    Tiempo O(N + M), con M = total de elementos listados en "cubre".
    """
    for campo in ("k", "B", "nodos"):
        if campo not in datos:
            raise ErrorDeFormato(f"falta el campo '{campo}'")
    k = _exigir_entero(datos["k"], "k")
    B = _exigir_entero(datos["B"], "B")
    if not isinstance(datos["nodos"], list):
        raise ErrorDeFormato("'nodos' debe ser una lista")

    nodos = []
    for posicion, d in enumerate(datos["nodos"]):
        for campo in ("id", "cubre", "utilidad"):
            if campo not in d:
                raise ErrorDeFormato(f"al nodo en la posición {posicion} le falta '{campo}'")
        id_nodo = _exigir_entero(d["id"], f"nodos[{posicion}].id")
        if not isinstance(d["cubre"], list):
            raise ErrorDeFormato(f"'cubre' del nodo {id_nodo} debe ser una lista")
        try:
            utilidad = crear_utilidad(d["utilidad"])
        except (KeyError, ValueError, TypeError) as error:
            raise ErrorDeFormato(f"utilidad del nodo {id_nodo}: {error}") from error
        nodos.append(Nodo(id_nodo, d["cubre"], utilidad))
    return Instancia(k, B, nodos, nombre)


def leer_instancia(ruta):
    """Lee un archivo JSON y devuelve la Instancia. El nombre del caso es el del archivo."""
    with open(ruta, encoding="utf-8") as archivo:
        try:
            datos = json.load(archivo)
        except json.JSONDecodeError as error:
            raise ErrorDeFormato(f"{ruta} no es un JSON válido: {error}") from error
    nombre = str(ruta).replace("\\", "/").split("/")[-1].removesuffix(".json")
    return instancia_desde_diccionario(datos, nombre)
