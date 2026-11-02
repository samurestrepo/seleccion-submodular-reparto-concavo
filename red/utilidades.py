"""Funciones de utilidad u_i de la Parte 1 y su ganancia marginal Δ_i(x).

Familias (informe, sección 6.5):
- "log":   u(x) = a · ln(1 + x)
- "raiz":  u(x) = a · √x
- "tabla": u se da por la lista de ganancias de sus unidades sucesivas
           (sirve para los ejemplos del informe, como P: 9, 5, 2, 1).

Cada familia sabe revisar su propia forma con revisar_forma(B, tolerancia):
así verificacion.py no tiene que recorrer las B unidades de cada nodo.
"""

import math


def _es_numero_finito(valor):
    """True si valor es un int o float que cabe en un float finito. bool, NaN e Infinity no valen."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    try:
        return math.isfinite(float(valor))
    except OverflowError:   # un entero enorme, como 10**400, no cabe en un float
        return False


def _problema_del_coeficiente(a):
    """Motivo por el que a no sirve como coeficiente (None si es finito y > 0). Tiempo O(1)."""
    if not _es_numero_finito(a) or a <= 0:
        return f"a = {a!r} (se necesita un número finito con a > 0)"
    return None


class UtilidadLog:
    """u(x) = a · ln(1 + x). Creciente y cóncava si a > 0."""

    def __init__(self, a):
        self.tipo = "log"
        self.a = a

    def valor(self, x):
        """u(x). Tiempo O(1)."""
        return self.a * math.log(1 + x)

    def ganancia(self, x):
        """Δ(x) = u(x + 1) − u(x): lo que aporta la unidad número x + 1. Tiempo O(1)."""
        return self.valor(x + 1) - self.valor(x)

    def revisar_forma(self, B, tolerancia):
        """None si u es creciente y cóncava; si no, el motivo. Tiempo O(1), sin recorrer B.

        Basta mirar a: la derivada a/(1 + x) es positiva y baja al crecer x, para todo x.
        B y tolerancia no se usan; están para que las tres familias se llamen igual.
        """
        return _problema_del_coeficiente(self.a)

    def describir(self):
        """Los datos de esta utilidad, en la misma forma del archivo de entrada."""
        return {"tipo": self.tipo, "a": self.a}


class UtilidadRaiz:
    """u(x) = a · √x. Creciente y cóncava si a > 0."""

    def __init__(self, a):
        self.tipo = "raiz"
        self.a = a

    def valor(self, x):
        """u(x). Tiempo O(1)."""
        return self.a * math.sqrt(x)

    def ganancia(self, x):
        """Δ(x) = u(x + 1) − u(x). Tiempo O(1)."""
        return self.valor(x + 1) - self.valor(x)

    def revisar_forma(self, B, tolerancia):
        """None si u es creciente y cóncava; si no, el motivo. Tiempo O(1), sin recorrer B.

        Basta mirar a: la derivada a/(2√x) es positiva y baja al crecer x, para todo x > 0.
        B y tolerancia no se usan; están para que las tres familias se llamen igual.
        """
        return _problema_del_coeficiente(self.a)

    def describir(self):
        """Los datos de esta utilidad, en la misma forma del archivo de entrada."""
        return {"tipo": self.tipo, "a": self.a}


class UtilidadTabla:
    """u dada por la lista de ganancias de sus unidades: [Δ(0), Δ(1), ...].

    Después de la última unidad de la lista, cada unidad extra aporta 0.
    u(x) se guarda acumulada (sumas prefijas) para responder en O(1).
    No se exige aquí que sea cóncava: eso lo revisa revisar_forma. Una tabla convexa
    se puede crear para llamar directamente a repartir_presupuesto (contraejemplo
    del informe, ver test_contraejemplo_convexo); por ejecutar.py se rechaza sin correr.
    """

    def __init__(self, ganancias):
        self.tipo = "tabla"
        self.ganancias = list(ganancias)
        self.acumulada = [0]
        for g in self.ganancias:
            self.acumulada.append(self.acumulada[-1] + g)

    def valor(self, x):
        """u(x) = Δ(0) + … + Δ(x − 1). Tiempo O(1)."""
        if x < len(self.acumulada):
            return self.acumulada[x]
        return self.acumulada[-1]

    def ganancia(self, x):
        """Δ(x); 0 si la lista ya se acabó. Tiempo O(1)."""
        if x < len(self.ganancias):
            return self.ganancias[x]
        return 0

    def revisar_forma(self, B, tolerancia):
        """None si u es creciente y cóncava en {0, …, B}; si no, el motivo.

        Solo importan las unidades que se pueden entregar: Δ(0), …, Δ(B − 1).
        Después de la lista todo vale 0, así que basta recorrerla una vez.
        Tiempo O(min(L, B)), con L el largo de la lista.
        """
        for x in range(min(B, len(self.ganancias))):
            if self.ganancia(x) < -tolerancia:
                return f"Δ({x}) < 0 (no es creciente)"
            if x + 1 < B and self.ganancia(x + 1) > self.ganancia(x) + tolerancia:
                return f"Δ({x + 1}) > Δ({x}) (no es cóncava)"
        return None

    def describir(self):
        """Los datos de esta utilidad, en la misma forma del archivo de entrada."""
        return {"tipo": self.tipo, "ganancias": self.ganancias}


def _coeficiente_valido(descripcion):
    """Devuelve "a" como float. Lanza ValueError si no es un número finito > 0. Tiempo O(1)."""
    problema = _problema_del_coeficiente(descripcion["a"])
    if problema is not None:
        raise ValueError(problema)
    return float(descripcion["a"])


def _ganancias_validas(descripcion):
    """Devuelve la lista "ganancias". Lanza ValueError si hay algo que no sea número finito. O(L)."""
    ganancias = descripcion["ganancias"]
    if not isinstance(ganancias, list):
        raise ValueError("'ganancias' debe ser una lista")
    for g in ganancias:
        if not _es_numero_finito(g):
            raise ValueError(f"cada ganancia debe ser un número finito; llegó {g!r}")
    return ganancias


def crear_utilidad(descripcion):
    """Construye una utilidad a partir de su descripción en el archivo de entrada.

    Recibe un diccionario como {"tipo": "log", "a": 9.0}.
    Devuelve el objeto de la familia correspondiente.
    Lanza ValueError si el tipo no se reconoce o los números no sirven
    (a debe ser finito y > 0; las ganancias, finitas), y KeyError si falta un campo.
    """
    tipo = descripcion.get("tipo")
    if tipo == "log":
        return UtilidadLog(_coeficiente_valido(descripcion))
    if tipo == "raiz":
        return UtilidadRaiz(_coeficiente_valido(descripcion))
    if tipo == "tabla":
        return UtilidadTabla(_ganancias_validas(descripcion))
    raise ValueError(f"tipo de utilidad desconocido: {tipo!r} (se esperaba log, raiz o tabla)")
