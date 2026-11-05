"""Fuerza bruta SOLO para las pruebas (instancias pequeñas).

No es el "algoritmo exacto" de la entrega de las semanas 5–6; sirve para
comprobar que el voraz de la Parte 1 es óptimo y que el de la Parte 2 respeta (1 − 1/e).
"""

from itertools import combinations


def repartos(n, B):
    """Todas las formas de escribir B como suma ordenada de n enteros ≥ 0."""
    if n == 1:
        yield (B,)
        return
    for primero in range(B + 1):
        for resto in repartos(n - 1, B - primero):
            yield (primero,) + resto


def mejor_reparto(S, B, utilidades):
    """Máximo de Σ u_i(x_i) probando todos los repartos."""
    return max(sum(utilidades[i].valor(x) for i, x in zip(S, reparto))
               for reparto in repartos(len(S), B))


def mejor_reparto_con_topes(S, B, utilidades, topes):
    """Máximo de Σ u_i(x_i) con x_i ≤ c_i, gastando mín(B, Σ c_i). Un nodo sin entrada en topes no tiene tope."""
    total = min(B, sum(topes.get(i, B) for i in S))
    return max(sum(utilidades[i].valor(x) for i, x in zip(S, reparto))
               for reparto in repartos(len(S), total)
               if all(x <= topes.get(i, B) for i, x in zip(S, reparto)))


def mejor_seleccion(conjuntos, k):
    """Máximo de f(S) = |unión| sobre todos los S de tamaño k."""
    mejor = 0
    for S in combinations(sorted(conjuntos), k):
        cubiertos = set()
        for v in S:
            cubiertos |= conjuntos[v]
        mejor = max(mejor, len(cubiertos))
    return mejor
