"""Parte 2, algoritmo EXACTO por fuerza bruta: sirve de referencia (OPT) para medir al voraz.

Recorre todos los subconjuntos de tamaño exactamente k de V y se queda con el de mayor f.
No es parte de la ronda: solo se usa para comprobar la garantía del voraz y para la tabla de la cota.
"""

from itertools import combinations
from math import comb

LIMITE_COMBINACIONES = 200000   # por encima de esto la fuerza bruta se niega a correr


class DemasiadasCombinaciones(Exception):
    """C(N, k) supera el límite: la fuerza bruta no se ejecuta."""


def seleccionar_exacto(oraculo, V, k):
    """Devuelve (S*, OPT, evaluaciones): el mejor subconjunto de tamaño k, f(S*) y cuántas veces se evaluó f.

    Recibe: un oráculo con `valor(S)` (cobertura o influencia), V (ids en orden creciente) y k.
    Orden: `combinations` entrega los subconjuntos en orden lexicográfico de ids (V ordenado).
    Empates: solo se reemplaza al mejor con f estrictamente mayor, así gana el primero en ese orden.
    Complejidad: exactamente C(N, k) evaluaciones de f; si C(N, k) > 200000 lanza DemasiadasCombinaciones.
    """
    total = comb(len(V), k)
    if total > LIMITE_COMBINACIONES:
        raise DemasiadasCombinaciones(
            f"C({len(V)}, {k}) = {total} supera el límite de {LIMITE_COMBINACIONES} "
            "subconjuntos: la fuerza bruta no se ejecuta"
        )
    mejor_S = None
    mejor_valor = float("-inf")
    evaluaciones = 0
    for S in combinations(V, k):
        valor = oraculo.valor(list(S))        # una evaluación de f(S) desde cero
        evaluaciones += 1
        if valor > mejor_valor:               # '>' estricto: el empate lo gana el primero lexicográfico
            mejor_S = list(S)
            mejor_valor = valor
    return mejor_S, mejor_valor, evaluaciones
