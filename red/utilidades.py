"""Funciones de utilidad u_i de la Parte 1 y su ganancia marginal Δ_i(x).

Familias (informe, sección 6.5):
- "log":   u(x) = a · ln(1 + x)
- "raiz":  u(x) = a · √x
- "tabla": u se da por la lista de ganancias de sus unidades sucesivas
           (sirve para los ejemplos del informe, como P: 9, 5, 2, 1).
"""

import math


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

    def describir(self):
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

    def describir(self):
        return {"tipo": self.tipo, "a": self.a}


class UtilidadTabla:
    """u dada por la lista de ganancias de sus unidades: [Δ(0), Δ(1), ...].

    Después de la última unidad de la lista, cada unidad extra aporta 0.
    u(x) se guarda acumulada (sumas prefijas) para responder en O(1).
    No se exige aquí que sea cóncava: eso lo revisa verificacion.py
    (así se puede correr el contraejemplo convexo del informe).
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

    def describir(self):
        return {"tipo": self.tipo, "ganancias": self.ganancias}


def crear_utilidad(descripcion):
    """Construye una utilidad a partir de su descripción en el archivo de entrada.

    Recibe un diccionario como {"tipo": "log", "a": 9.0}.
    Devuelve el objeto de la familia correspondiente. Lanza ValueError si no se reconoce.
    """
    tipo = descripcion.get("tipo")
    if tipo == "log":
        return UtilidadLog(float(descripcion["a"]))
    if tipo == "raiz":
        return UtilidadRaiz(float(descripcion["a"]))
    if tipo == "tabla":
        return UtilidadTabla(descripcion["ganancias"])
    raise ValueError(f"tipo de utilidad desconocido: {tipo!r} (se esperaba log, raiz o tabla)")
