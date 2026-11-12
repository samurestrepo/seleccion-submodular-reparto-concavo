"""Parte 1 por programación dinámica (referencia): reparto exacto aun si alguna u_i no es cóncava.

El voraz de `reparto.py` es óptimo solo con u_i crecientes y cóncavas. Esta PD no usa esa hipótesis:
prueba todas las cantidades t que podría recibir cada nodo, así que sirve de contraste (y de óptimo
en el caso convexo, donde el voraz falla). Cuesta mucho más: Θ(N·B²) en el peor caso.

Recurrencia (bottom-up). M[i][b] = mejor utilidad repartiendo A LO SUMO b unidades entre los nodos 1..i:
    M[0][b] = 0                                        para todo b (sin nodos, la utilidad es 0)
    M[i][b] = máx sobre t = 0..mín(c_i, b) de  u_i(t) + M[i−1][b − t]
P[i][b] guarda el t ganador; ante empate, el MENOR t (se recorre t en orden creciente y solo se
reemplaza con `>` estricto). La respuesta es M[N][B] y x se reconstruye desde (N, B) hacia atrás.
"""


class ResultadoPD:
    """Lo que devuelve la PD: x, la utilidad total y cuántos candidatos t se evaluaron."""

    def __init__(self, x, utilidad, candidatos):
        self.x = x                    # diccionario id → unidades asignadas
        self.utilidad = utilidad      # Σ u_i(x_i) = M[N][B]
        self.candidatos = candidatos  # veces que se evaluó u_i(t) + M[i−1][b−t] (un candidato t)


def repartir_pd(S, B, utilidades, topes=None):
    """Reparte hasta B unidades entre los nodos de S por PD, con x_i ≤ c_i. Sirve con u_i no cóncavas.

    Recibe: S (ids sin repetir), B ≥ 0, diccionario id → utilidad (interfaz valor(t), como
    reparto.py) y topes opcional (id → c_i; sin tope, c_i = B). Σ x_i ≤ B: M[i][b] es "a lo sumo b
    unidades", así que si Σ c_i < B sobra presupuesto, igual que en el voraz. Con u_i crecientes la
    utilidad coincide con la del voraz, que gasta mín(B, Σ c_i); el vector x puede diferir por empates.
    Devuelve: ResultadoPD (x, utilidad, candidatos).
    Complejidad: T = Σ_i Σ_b (mín(c_i, b) + 1) candidatos, cada uno O(1). Peor caso, con c_i ≥ B,
    T = N·(B + 1)(B + 2)/2 = Θ(N·B²); mejor caso, con todos los topes en 0, T = N·(B + 1) = Θ(N·B).
    Espacio Θ(N·B) por la tabla P (de M solo se guardan dos filas).
    """
    if B > 0 and len(S) == 0:
        raise ValueError("no hay nodos a quienes repartir el presupuesto")

    topes = topes or {}
    candidatos = 0
    anterior = [0.0] * (B + 1)                      # fila M[0][·]: sin nodos, utilidad 0
    elegido = []                                    # P[i][b] de cada nodo, en el orden de S

    for i in S:
        tope = min(topes.get(i, B), B)              # c_i; sin tope, B
        valores = [utilidades[i].valor(t) for t in range(tope + 1)]   # u_i(0..c_i), una sola vez
        actual = [0.0] * (B + 1)
        fila_p = [0] * (B + 1)
        for b in range(B + 1):
            mejor, mejor_t = None, 0
            for t in range(min(tope, b) + 1):       # t en orden creciente: gana el menor en empate
                candidatos += 1
                candidato = valores[t] + anterior[b - t]
                if mejor is None or candidato > mejor:
                    mejor, mejor_t = candidato, t
            actual[b] = mejor
            fila_p[b] = mejor_t
        elegido.append(fila_p)
        anterior = actual

    x = {i: 0 for i in S}                           # reconstrucción desde (N, B) hacia atrás
    restante = B
    for posicion in range(len(S) - 1, -1, -1):
        t = elegido[posicion][restante]
        x[S[posicion]] = t
        restante -= t
    return ResultadoPD(x, anterior[B], candidatos)
