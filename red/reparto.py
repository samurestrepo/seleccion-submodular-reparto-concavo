"""Parte 1: algoritmo voraz de reparto con montículo (REPARTIR-PRESUPUESTO, informe 6.4).

Entrega el presupuesto unidad por unidad; cada unidad va al nodo cuya siguiente
unidad aporta más. Es óptimo porque cada u_i es creciente y cóncava.

MONTÍCULO DE MÁXIMOS CON heapq:
heapq de Python es un montículo de MÍNIMOS (la raíz es la clave más pequeña).
Para que la raíz sea la MAYOR ganancia se guarda la pareja (−ganancia, índice):
la ganancia más grande tiene el negativo más pequeño y queda en la raíz.
Si dos ganancias empatan, Python compara el segundo elemento de la pareja,
el índice, y sale primero el MENOR índice: ese es el desempate del informe.
"""

import heapq


class ResultadoReparto:
    """Lo que devuelve el reparto: x, la utilidad total y los contadores del montículo."""

    def __init__(self, x, utilidad, extracciones, inserciones):
        self.x = x                        # diccionario id → unidades asignadas
        self.utilidad = utilidad          # Σ u_i(x_i)
        self.extracciones = extracciones  # veces que se hizo EXTRAER-MÁXIMO (debe ser B)
        self.inserciones = inserciones    # veces que se hizo INSERTAR (debe ser B)


def repartir_presupuesto(S, B, utilidades, traza=None):
    """Reparte B unidades entre los nodos de S para maximizar Σ u_i(x_i).

    Recibe: S (ids de los nodos elegidos), B y el diccionario id → utilidad; traza opcional.
    Devuelve: ResultadoReparto.
    Complejidad: O(N + B lg N) en el peor caso, Θ(N + B) en el mejor, con N = |S|.
    Espacio Θ(N): el montículo y x tienen un elemento por nodo.
    """
    if B > 0 and len(S) == 0:
        raise ValueError("no hay nodos a quienes repartir el presupuesto")

    x = {}
    for i in S:                                              # línea 1
        x[i] = 0

    H = [(-utilidades[i].ganancia(0), i) for i in S]         # línea 2: parejas (−Δ_i(0), i)
    heapq.heapify(H)                                         # línea 2: BUILD-HEAP en O(N)
    extracciones = 0
    inserciones = 0

    for unidad in range(1, B + 1):                           # línea 3
        menos_delta, i = heapq.heappop(H)                    # línea 4: EXTRAER-MÁXIMO, O(lg N)
        extracciones += 1
        delta = -menos_delta                                 # se deshace el signo
        x[i] = x[i] + 1                                      # línea 5
        siguiente = utilidades[i].ganancia(x[i])             # Δ_i de la próxima unidad de i
        heapq.heappush(H, (-siguiente, i))                   # línea 6: INSERTAR, O(lg N)
        inserciones += 1
        if traza is not None:                                # línea 7
            traza.unidad_reparto(unidad, i, delta)

    utilidad = sum(utilidades[i].valor(x[i]) for i in S)     # línea 8
    return ResultadoReparto(x, utilidad, extracciones, inserciones)
