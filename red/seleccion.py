"""Parte 2: algoritmo voraz de selección (SELECCIONAR-NODOS, informe 6.3).

En k pasos, agrega al equipo el nodo de mayor ganancia marginal Δ(v | S).
Empates: gana el de menor índice (se recorre V en orden creciente y solo se
reemplaza al mejor con un Δ estrictamente mayor).

Garantía: f(S) ≥ (1 − 1/e)·OPT si f es monótona, submodular y f(∅) = 0
(Nemhauser, Wolsey y Fisher, 1978).
"""


def seleccionar_nodos(oraculo, V, k, traza=None):
    """Elige k nodos con el voraz y devuelve (S, valorS).

    Recibe: el oráculo de cobertura, V (ids en orden creciente), k y una traza opcional.
    Devuelve: S como lista en el orden en que se eligieron, y valorS = f(S).
    Complejidad: k·N − k(k−1)/2 llamadas a Δ, o sea Θ(N·k) en todos los casos;
    con cobertura, O(k·M) en tiempo. Espacio adicional O(k + |U|).
    """
    S = []                     # línea 1 del pseudocódigo
    en_S = set()               # para preguntar "¿v está en S?" en O(1)
    cubiertos = set()          # cub(S): lo que ya cubre el equipo
    valorS = oraculo.valor(S)  # línea 1: valorS ← f(∅), que vale 0

    for paso in range(1, k + 1):                       # línea 2
        mejor = None                                   # línea 3
        mejor_delta = float("-inf")
        aportes = []                                   # para la traza: (v, Δ) de cada candidato
        for v in V:                                    # línea 4: v ∈ V \ S en orden creciente
            if v in en_S:
                continue
            delta = oraculo.ganancia(v, cubiertos)     # línea 5: una llamada al oráculo
            aportes.append((v, delta))
            if delta > mejor_delta:                    # línea 6: '>' estricto ⇒ desempata el menor índice
                mejor = v                              # línea 7
                mejor_delta = delta
        S.append(mejor)                                # línea 8
        en_S.add(mejor)
        cubiertos |= oraculo.conjunto(mejor)
        valorS = valorS + mejor_delta
        if traza is not None:                          # línea 9
            traza.paso_seleccion(paso, aportes, mejor, mejor_delta, valorS)

    return S, valorS                                   # línea 10
