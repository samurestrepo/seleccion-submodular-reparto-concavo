"""Lectura de una instancia desde un archivo JSON. Reconoce dos formatos:
- El de la profesora (decisiones 24 a 26): el objeto tiene "parametros", "grafo" y "nodos".
- El propio (provisional, informe 6.5): el objeto tiene "k", "B" y "nodos".

Es el ÚNICO archivo que conoce el formato de entrada.

Revisa la FORMA del archivo (campos, tipos y que los números de las utilidades sirvan).
Las restricciones del problema (k < N, concavidad, etc.) las revisa verificacion.py
y quedan en la traza. Cualquier problema de forma se reporta como ErrorDeFormato.
"""

import json

from red.cobertura import OraculoCobertura
from red.influencia import OraculoInfluencia
from red.utilidades import _es_numero_finito, crear_utilidad


class ErrorDeFormato(Exception):
    """El archivo no tiene la forma esperada."""


class Nodo:
    """Un nodo candidato: su identificador, lo que cubre (Parte 2) y su utilidad (Parte 1).

    costo_participacion y presupuesto_total solo existen en el formato de la profesora; el costo
    se guarda, pero la solución base no lo aplica (decisión 26). tope es c_i en x_i ≤ c_i: en la
    profesora sale de presupuesto_total; en el propio es opcional; None significa sin tope (decisión 28).
    """

    def __init__(self, id, cubre, utilidad, costo_participacion=None, presupuesto_total=None, tope=None):
        self.id = id
        self.cubre = frozenset(cubre)
        self.utilidad = utilidad
        self.costo_participacion = costo_participacion
        self.presupuesto_total = presupuesto_total
        self.tope = tope


class Instancia:
    """Un caso completo: k, B y la lista de nodos ordenada por id.

    vecinos (id → {vecino: peso}) y variantes (datos de las variantes que solo se reportan)
    vienen en el formato de la profesora; en el propio quedan en None.
    """

    def __init__(self, k, B, nodos, nombre="sin_nombre", vecinos=None, variantes=None):
        self.k = k
        self.B = B
        self.nodos = sorted(nodos, key=lambda nodo: nodo.id)
        self.nombre = nombre
        self.vecinos = vecinos
        self.variantes = variantes

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

    def topes(self):
        """Diccionario id → c_i, solo de los nodos que tienen tope (para la Parte 1). Tiempo O(N)."""
        return {nodo.id: nodo.tope for nodo in self.nodos if nodo.tope is not None}

    def crear_oraculo(self):
        """Un oráculo NUEVO, con sus contadores en cero, del tipo que corresponde a este formato.

        Influencia si hay grafo; si no, cobertura. Tiempo O(N).
        En influencia, a_w es el mismo coeficiente de la utilidad de w (decisiones 24 y 25).
        """
        if self.vecinos is None:
            return OraculoCobertura(self.conjuntos())
        coeficientes = {nodo.id: nodo.utilidad.a for nodo in self.nodos}
        return OraculoInfluencia(coeficientes, self.vecinos)

    def numero_aristas(self):
        """Aristas del grafo; 0 si el formato no trae grafo. Cada una está en sus dos puntas. O(N)."""
        if self.vecinos is None:
            return 0
        return sum(len(adyacentes) for adyacentes in self.vecinos.values()) // 2


def _exigir_entero(valor, campo):
    """Devuelve valor si es un entero. Un bool no cuenta. Si no, lanza ErrorDeFormato."""
    if not isinstance(valor, int) or isinstance(valor, bool):
        raise ErrorDeFormato(f"'{campo}' debe ser un entero; llegó {valor!r}")
    return valor


def _exigir_numero(valor, campo):
    """Devuelve valor si es un número finito. bool, NaN e Infinity no valen. Si no, ErrorDeFormato."""
    if not _es_numero_finito(valor):
        raise ErrorDeFormato(f"'{campo}' debe ser un número finito; llegó {valor!r}")
    return valor


def _exigir_tope(valor, campo):
    """Devuelve valor si sirve como tope: un entero ≥ 0, porque x_i es entero. Si no, ErrorDeFormato."""
    _exigir_entero(valor, campo)
    if valor < 0:
        raise ErrorDeFormato(f"'{campo}' no puede ser negativo; llegó {valor!r}")
    return valor


def _exigir_lista(valor, campo):
    """Devuelve valor si es una lista. Si no, lanza ErrorDeFormato."""
    if not isinstance(valor, list):
        raise ErrorDeFormato(f"'{campo}' debe ser una lista")
    return valor


def _exigir_campos(d, campos, donde):
    """Revisa que d sea un objeto y traiga todos los campos. Si no, lanza ErrorDeFormato."""
    if not isinstance(d, dict):
        raise ErrorDeFormato(f"{donde} debe ser un objeto; llegó {d!r}")
    for campo in campos:
        if campo not in d:
            raise ErrorDeFormato(f"a {donde} le falta '{campo}'")


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
    tope = None
    if "tope" in d:              # campo opcional: sin él, el nodo no tiene tope
        tope = _exigir_tope(d["tope"], f"nodos[{posicion}].tope")
    try:
        return Nodo(id_nodo, d["cubre"], utilidad, tope=tope)
    except TypeError as error:   # frozenset no acepta listas ni objetos como elementos
        raise ErrorDeFormato(f"'cubre' del nodo {id_nodo} no puede tener listas ni objetos") from error


def _leer_nodo_profesora(d, posicion):
    """Convierte un nodo del formato de la profesora en un Nodo. Tiempo O(1).

    El id se conserva como texto y u_i(x) = coeficiente_utilidad · ln(1 + x) (decisión 25).
    El tope del nodo es presupuesto_total_nodo (decisión 28).
    Lanza ErrorDeFormato si falta un campo, un valor no es numérico, el coeficiente no es > 0
    o presupuesto_total_nodo no es un entero ≥ 0.
    """
    _exigir_campos(d, ("id", "coeficiente_utilidad", "presupuesto_total_nodo", "costo_participacion"),
                   f"el nodo en la posición {posicion}")
    id_nodo = d["id"]
    if not isinstance(id_nodo, str):
        raise ErrorDeFormato(f"nodos[{posicion}].id debe ser un texto; llegó {id_nodo!r}")
    coeficiente = _exigir_numero(d["coeficiente_utilidad"], f"nodos[{posicion}].coeficiente_utilidad")
    campo_total = f"nodos[{posicion}].presupuesto_total_nodo"
    presupuesto_total = _exigir_tope(_exigir_numero(d["presupuesto_total_nodo"], campo_total), campo_total)
    costo = _exigir_numero(d["costo_participacion"], f"nodos[{posicion}].costo_participacion")
    try:
        utilidad = crear_utilidad({"tipo": "log", "a": coeficiente})
    except ValueError as error:   # coeficiente ≤ 0 (decisión 17)
        raise ErrorDeFormato(f"utilidad del nodo {id_nodo}: {error}") from error
    return Nodo(id_nodo, [], utilidad, costo, presupuesto_total, tope=presupuesto_total)


def _leer_grafo(aristas, ids):
    """Convierte la lista de aristas en id → {vecino: peso}, con cada arista en sus dos puntas.

    Lanza ErrorDeFormato si una arista nombra un nodo inexistente, es un lazo o está repetida
    ({u, v} y {v, u} son la misma: el grafo no es dirigido). Tiempo O(N + A) esperado, con A = aristas.
    El rango [0, 1] del peso no se revisa aquí: es una restricción y la revisa verificacion.py.
    """
    vecinos = {i: {} for i in ids}
    for posicion, arista in enumerate(aristas):
        _exigir_campos(arista, ("u", "v", "peso_influencia"), f"la arista en la posición {posicion}")
        u, v = arista["u"], arista["v"]
        for extremo in (u, v):
            if not isinstance(extremo, str) or extremo not in vecinos:
                raise ErrorDeFormato(f"la arista en la posición {posicion} nombra un nodo inexistente: {extremo!r}")
        if u == v:
            raise ErrorDeFormato(f"la arista en la posición {posicion} es un lazo sobre {u}")
        if v in vecinos[u]:
            raise ErrorDeFormato(f"la arista {{{u}, {v}}} está repetida (posición {posicion})")
        peso = _exigir_numero(arista["peso_influencia"], f"grafo[{posicion}].peso_influencia")
        vecinos[u][v] = peso
        vecinos[v][u] = peso
    return vecinos


def _instancia_de_la_profesora(datos, nombre):
    """Convierte el formato de la profesora en una Instancia (decisiones 24 a 26).

    Recibe {"parametros": {...}, "grafo": [{"u", "v", "peso_influencia"}, ...],
    "nodos": [{"id", "coeficiente_utilidad", "presupuesto_total_nodo", "costo_participacion"}, ...]}.
    Lanza ErrorDeFormato si algo no cuadra. Tiempo O(N lg N + A), por ordenar los nodos.
    """
    _exigir_campos(datos, ("parametros", "grafo", "nodos"), "el archivo")
    p = datos["parametros"]
    _exigir_campos(p, ("numero_nodos", "numero_rondas", "cupo_participantes_por_ronda_k",
                       "presupuesto_ruido_por_ronda_B", "presupuesto_costos_participacion_por_ronda"),
                   "'parametros'")
    numero_nodos = _exigir_entero(p["numero_nodos"], "numero_nodos")
    k = _exigir_entero(p["cupo_participantes_por_ronda_k"], "cupo_participantes_por_ronda_k")
    B = _exigir_entero(p["presupuesto_ruido_por_ronda_B"], "presupuesto_ruido_por_ronda_B")
    variantes = {
        "numero_rondas": _exigir_entero(p["numero_rondas"], "numero_rondas"),
        "presupuesto_costos_participacion_por_ronda": _exigir_numero(
            p["presupuesto_costos_participacion_por_ronda"], "presupuesto_costos_participacion_por_ronda"),
    }
    nodos = [_leer_nodo_profesora(d, posicion)
             for posicion, d in enumerate(_exigir_lista(datos["nodos"], "nodos"))]
    if numero_nodos != len(nodos):
        raise ErrorDeFormato(f"numero_nodos = {numero_nodos}, pero la lista trae {len(nodos)} nodos")
    vecinos = _leer_grafo(_exigir_lista(datos["grafo"], "grafo"), [nodo.id for nodo in nodos])
    return Instancia(k, B, nodos, nombre, vecinos, variantes)


def instancia_desde_diccionario(datos, nombre="sin_nombre"):
    """Convierte el contenido leído del JSON en una Instancia, según el formato que traiga.

    Si el objeto tiene "parametros", es el de la profesora. Si no, es el propio:
    {"k": int, "B": int, "nodos": [{"id", "cubre", "utilidad"}, ...]}.
    Devuelve: Instancia. Lanza ErrorDeFormato si falta un campo o un tipo no cuadra.
    Tiempo del formato propio: O(N + M + ΣL), con M = total de elementos en "cubre" y L = largo de cada tabla.
    """
    if not isinstance(datos, dict):
        raise ErrorDeFormato(f"el archivo debe ser un objeto con k, B y nodos; llegó {datos!r}")
    if "parametros" in datos:
        return _instancia_de_la_profesora(datos, nombre)
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
