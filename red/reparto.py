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
        self.extracciones = extracciones  # veces que se hizo EXTRAER-MÁXIMO (sin topes, B)
        self.inserciones = inserciones    # veces que se hizo INSERTAR (sin topes, B)


def repartir_presupuesto(S, B, utilidades, traza=None, topes=None):
    """Reparte hasta B unidades entre los nodos de S para maximizar Σ u_i(x_i), con x_i ≤ c_i.

    Recibe: S (ids de los nodos elegidos, sin repetir), B y el diccionario id → utilidad; traza opcional;
    topes opcional (id → c_i; un nodo que no aparece no tiene tope). Si Σ c_i < B, sobra presupuesto.
    Precondiciones: B ≥ 0, c_i entero ≥ 0 y cada u_i creciente y cóncava (si no, no hay garantía de óptimo).
    Aquí no se comprueban, para seguir el pseudocódigo; las valida ronda.py.
    Devuelve: ResultadoReparto.
    Complejidad, con N = |S|: peor caso O(N + B lg N). Sin topes y con heapq es Θ(N + B(1 + lg N)) para
    toda entrada, porque heappop siempre baja hasta una hoja. El 1 cubre N = 1: lg 1 = 0, pero el ciclo
    igual da B vueltas. Con topes, a lo sumo B vueltas y el montículo solo se achica. Espacio Θ(N).
    """
    if B > 0 and len(S) == 0:
        raise ValueError("no hay nodos a quienes repartir el presupuesto")

    topes = topes or {}
    sin_tope = float("inf")

    x = {}
    for i in S:                                              # línea 1 del pseudocódigo
        x[i] = 0

    # línea 2 del pseudocódigo: parejas (−Δ_i(0), i); un nodo con tope 0 no entra al montículo
    H = [(-utilidades[i].ganancia(0), i) for i in S if topes.get(i, sin_tope) > 0]
    heapq.heapify(H)                                         # línea 2 del pseudocódigo: BUILD-HEAP en O(N)
    extracciones = 0
    inserciones = 0

    for unidad in range(1, B + 1):                           # línea 3 del pseudocódigo
        if not H:                                            # todos llegaron a su tope: sobra presupuesto
            break
        menos_delta, i = heapq.heappop(H)                    # línea 4 del pseudocódigo: EXTRAER-MÁXIMO, O(lg N)
        extracciones += 1
        delta = -menos_delta                                 # se deshace el signo
        x[i] = x[i] + 1                                      # línea 5 del pseudocódigo
        if x[i] < topes.get(i, sin_tope):                    # el que llegó a su tope no vuelve al montículo
            siguiente = utilidades[i].ganancia(x[i])         # Δ_i de la próxima unidad de i
            heapq.heappush(H, (-siguiente, i))               # línea 6 del pseudocódigo: INSERTAR, O(lg N)
            inserciones += 1
        if traza is not None:                                # línea 7 del pseudocódigo
            traza.unidad_reparto(unidad, i, delta)

    utilidad = sum(utilidades[i].valor(x[i]) for i in S)     # línea 8 del pseudocódigo
    return ResultadoReparto(x, utilidad, extracciones, inserciones)
