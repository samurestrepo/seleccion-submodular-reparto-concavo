"""Oráculo f de la Parte 2: la función de cobertura.

f(S) = número de elementos distintos que cubren juntos los nodos de S (informe 5.4).
Δ(v | S) = |C_v ∖ cub(S)|: los elementos de v que el equipo todavía no cubría (informe 5.6).

El costo de la Parte 2 se mide en llamadas al oráculo, por eso se cuentan.
"""


class OraculoCobertura:
    """Guarda el conjunto C_v de cada nodo y cuenta cuántas veces se le consulta."""

    def __init__(self, conjuntos):
        """conjuntos: diccionario id → conjunto de elementos que cubre ese nodo."""
        self.conjuntos = conjuntos
        self.llamadas_ganancia = 0   # evaluaciones de Δ(v | S): la operación básica del voraz
        self.llamadas_valor = 0      # evaluaciones de f(S) desde cero

    def estado_inicial(self):
        """El estado del equipo vacío: cub(∅), un set sin elementos. Tiempo O(1)."""
        return set()

    def agregar(self, estado, v):
        """Actualiza cub(S) EN SU LUGAR cuando v entra al equipo y lo devuelve. No cuenta como llamada.

        Tiempo O(|C_v|).
        """
        estado |= self.conjuntos[v]
        return estado

    def valor(self, S):
        """f(S) calculada desde cero: tamaño de la unión de los C_v con v en S.

        Tiempo O(Σ_{v ∈ S} |C_v|). Se usa en f(∅) y en la verificación.
        """
        self.llamadas_valor += 1
        cubiertos = set()
        for v in S:
            cubiertos |= self.conjuntos[v]
        return len(cubiertos)

    def ganancia(self, v, estado):
        """Δ(v | S) = |C_v ∖ cub(S)|, donde `estado` es cub(S) ya calculado.

        Recorre una sola vez los elementos de C_v: tiempo O(|C_v|)
        (cada consulta 'e in estado' es O(1) esperado en un set).
        Es una llamada al oráculo (línea 5 del pseudocódigo de SELECCIONAR-NODOS).
        """
        self.llamadas_ganancia += 1
        nuevos = 0
        for elemento in self.conjuntos[v]:
            if elemento not in estado:
                nuevos += 1
        return nuevos
