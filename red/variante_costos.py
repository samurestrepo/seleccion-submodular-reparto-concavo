"""Variante (a) de la Parte 2: selección con costos de participación (restricción de mochila).

Cada nodo v tiene un costo c(v) > 0 y hay un presupuesto de participación L. Se busca S ⊆ V
que maximice f(S) con Σ_{v∈S} c(v) ≤ L. **Supuesto ❓:** esta restricción REEMPLAZA a |S| ≤ k;
no se usan las dos a la vez (decisión 35). f es la misma de la solución base (cobertura o
influencia): monótona, submodular y con f(∅) = 0, a través del oráculo con estado explícito
(`estado_inicial`, `ganancia`, `agregar`, `valor`).

Cuatro algoritmos, todos con contadores explícitos de evaluaciones de f:
1. `seleccionar_exacto_costos`: fuerza bruta sobre los 2^N subconjuntos (referencia, OPT).
2. `voraz_por_cociente`: en cada paso toma, entre los que caben, el de mayor Δ(v | S) / c(v).
   Sin garantía constante (ver el contraejemplo en las pruebas).
3. `voraz_modificado`: el mejor entre el voraz por cociente y el mejor nodo solo que quepa.
   Garantía (1 − 1/e)/2 ≈ 0,316 (Khuller, Moss y Naor, 1999), mejorada a 0,405 para f monótona
   y submodular con restricción de mochila (Tang et al., 2021).
4. `enumeracion_parcial`: todos los subconjuntos factibles de tamaño ≤ 2 y, desde cada subconjunto
   factible de 3 nodos, se completa con el voraz por cociente. Garantía 1 − 1/e con O(n⁵)
   evaluaciones de f (Sviridenko, 2004).

Empates: siempre gana el primero en el orden de recorrido (ids crecientes, `>` estricto), como en
la solución base (decisión 6).

Referencias:
- Khuller, S., Moss, A. y Naor, J. (1999). The budgeted maximum coverage problem.
  Information Processing Letters, 70(1), 39–45. https://doi.org/10.1016/S0020-0190(99)00031-9
- Sviridenko, M. (2004). A note on maximizing a submodular set function subject to a knapsack
  constraint. Operations Research Letters, 32(1), 41–43. https://doi.org/10.1016/S0167-6377(03)00062-2
- Tang, J., Tang, X., Lim, A., Han, K., Li, C. y Yuan, J. (2021). Revisiting modified greedy algorithm
  for monotone submodular maximization with a knapsack constraint. Proceedings of the ACM on
  Measurement and Analysis of Computing Systems, 5(1), artículo 8. https://doi.org/10.1145/3447386
"""

from itertools import combinations

from red.exacto import LIMITE_COMBINACIONES, DemasiadasCombinaciones

TAMANO_ENUMERADO = 3   # Sviridenko: se enumeran los subconjuntos de tamaño ≤ 2 y se completa desde los de tamaño 3


class ResultadoCostos:
    """Lo que devuelve cada algoritmo de la variante (a): S, f(S), el costo de S y las evaluaciones.

    `evaluaciones` cuenta las llamadas a `ganancia` y a `valor` que hizo el algoritmo (la operación
    básica de la Parte 2). `origen` solo lo llena el voraz modificado: "cociente" o "mejor_nodo_solo".
    `mejor_solo` es (v, f({v})) del mejor nodo que cabe solo; lo llena el voraz por cociente sin costo
    extra, porque f({v}) = Δ(v | ∅) ya se evaluó en su primer paso. None si ningún nodo cabe.
    """

    def __init__(self, S, valor, costo, evaluaciones, origen=None, mejor_solo=None):
        self.S = S                        # lista de ids, en el orden en que entraron
        self.valor = valor                # f(S)
        self.costo = costo                # Σ_{v∈S} c(v)
        self.evaluaciones = evaluaciones  # llamadas a ganancia + llamadas a valor
        self.origen = origen
        self.mejor_solo = mejor_solo


def seleccionar_exacto_costos(oraculo, V, costos, L):
    """Fuerza bruta con presupuesto: devuelve (S*, OPT, evaluaciones) sobre los subconjuntos factibles.

    Recibe: oráculo con `valor(S)`, V (ids en orden creciente), costos (id → c(v) > 0) y L ≥ 0.
    Recorre los subconjuntos en orden lexicográfico de ids con una búsqueda en profundidad
    (∅, {v1}, {v1, v2}, …) y poda: si S no cabe, ningún superconjunto cabe, porque los costos son
    positivos. Evalúa f solo en los factibles; en los empates gana el primero en ese orden (`>` estricto).
    Complejidad: evaluaciones = número F de subconjuntos factibles (incluido ∅), F ≤ 2^N; visita a lo
    sumo F·(N + 1) subconjuntos. Peor caso (L ≥ Σ c): Θ(2^N) evaluaciones; mejor caso (L < c_mín):
    1 evaluación y Θ(N) tiempo. Espacio O(N) (la pila de la búsqueda y S), más el del oráculo.
    Se niega (DemasiadasCombinaciones) si 2^N > LIMITE_COMBINACIONES, sin evaluar nada.
    """
    total = 2 ** len(V)
    if total > LIMITE_COMBINACIONES:
        raise DemasiadasCombinaciones(
            f"2^{len(V)} = {total} supera el límite de {LIMITE_COMBINACIONES} "
            "subconjuntos: la fuerza bruta con presupuesto no se ejecuta"
        )
    mejor = {"S": [], "valor": float("-inf"), "evaluaciones": 0}

    def explorar(S, costo_S, desde):
        """Evalúa S (factible por construcción) y extiende con cada id de V[desde:] que quepa."""
        valor = oraculo.valor(list(S))           # una evaluación de f(S) desde cero
        mejor["evaluaciones"] += 1
        if valor > mejor["valor"]:               # '>' estricto: el empate lo gana el primero lexicográfico
            mejor["S"] = list(S)
            mejor["valor"] = valor
        for posicion in range(desde, len(V)):
            v = V[posicion]
            if costo_S + costos[v] <= L:         # poda: si v no cabe, tampoco cabe nada que lo contenga
                S.append(v)
                explorar(S, costo_S + costos[v], posicion + 1)
                S.pop()

    explorar([], 0, 0)
    return mejor["S"], mejor["valor"], mejor["evaluaciones"]


def voraz_por_cociente(oraculo, V, costos, L, traza=None, inicial=()):
    """Voraz por cociente: en cada paso agrega, entre los nodos que todavía caben, el de mayor Δ(v | S)/c(v).

    Recibe: oráculo, V (ids en orden creciente), costos (id → c(v) > 0), L, traza opcional y un
    conjunto inicial (lo usa la enumeración parcial; vacío en el uso normal).
    Los nodos que no caben se saltan sin evaluarlos; el ciclo termina cuando ninguno cabe.
    Devuelve ResultadoCostos; `mejor_solo` trae el mejor nodo que cabe solo, sacado del paso 1
    (f({v}) = Δ(v | ∅)) sin evaluaciones extra, y solo si `inicial` está vacío.
    Complejidad: el paso j evalúa a lo sumo N − j + 1 candidatos, así que
    evaluaciones ≤ |S|·N − |S|(|S| − 1)/2, con |S| ≤ mín(N, ⌊L / c_mín⌋): O(N · mín(N, L/c_mín)).
    Peor caso (L ≥ Σ c, todo cabe siempre): exactamente N(N + 1)/2 evaluaciones, Θ(N²).
    Mejor caso (L < c_mín): 0 evaluaciones y Θ(N) tiempo (un recorrido de V).
    Con influencia cada evaluación cuesta O(1 + grado(v)): un paso cuesta O(N + A) y el total
    O(|S| · (N + A)). Espacio O(N) (S, en_S) más el estado del oráculo.
    Con `inicial` = T: una evaluación más (f(T) con `valor`) y los pasos arrancan desde T.
    """
    S = list(inicial)
    en_S = set(S)
    estado = oraculo.estado_inicial()
    for v in S:
        estado = oraculo.agregar(estado, v)      # no cuenta: `agregar` no evalúa f
    valorS = oraculo.valor(S)                    # f(inicial): f(∅) = 0 si está vacío
    costo_S = sum(costos[v] for v in S)
    evaluaciones = 1
    mejor_solo = None

    paso = 0
    while True:
        paso += 1
        mejor, mejor_delta, mejor_cociente = None, None, float("-inf")
        aportes = []                             # solo con traza: (v, Δ, c(v)) de cada candidato
        for v in V:                              # ids en orden creciente ⇒ el empate lo gana el menor
            if v in en_S or costo_S + costos[v] > L:
                continue                         # ya está en S, o no cabe: se salta sin evaluar
            delta = oraculo.ganancia(v, estado)  # una evaluación de Δ(v | S)
            evaluaciones += 1
            if traza is not None:
                aportes.append((v, delta, costos[v]))
            if paso == 1 and not inicial and (mejor_solo is None or delta > mejor_solo[1]):
                mejor_solo = (v, delta)          # f({v}) = Δ(v | ∅): el mejor nodo solo, gratis
            if delta / costos[v] > mejor_cociente:   # '>' estricto ⇒ desempata el menor índice
                mejor, mejor_delta, mejor_cociente = v, delta, delta / costos[v]
        if mejor is None:                        # ningún candidato cabe: fin
            break
        S.append(mejor)
        en_S.add(mejor)
        estado = oraculo.agregar(estado, mejor)
        valorS = valorS + mejor_delta
        costo_S += costos[mejor]
        if traza is not None:
            traza.paso_seleccion_costos(paso, aportes, mejor, mejor_delta, valorS, costo_S)

    return ResultadoCostos(S, valorS, costo_S, evaluaciones, mejor_solo=mejor_solo)


def voraz_modificado(oraculo, V, costos, L, traza=None):
    """Voraz modificado (Khuller, Moss y Naor, 1999): el mejor entre el voraz por cociente y el mejor nodo solo.

    Recibe lo mismo que `voraz_por_cociente`. Devuelve ResultadoCostos con `origen` = "cociente" o
    "mejor_nodo_solo"; en empate se queda con el del cociente (ya es ≥ el nodo solo si lo contiene).
    Garantía: f(S) ≥ 0,405 · OPT para f monótona y submodular (Tang et al., 2021); la original es
    (1 − 1/e)/2 (Khuller et al., 1999).
    Complejidad: las mismas evaluaciones que el voraz por cociente, sin ninguna extra, porque el mejor
    nodo solo sale del paso 1 (f({v}) = Δ(v | ∅)). Espacio O(N) más el estado del oráculo.
    """
    cociente = voraz_por_cociente(oraculo, V, costos, L, traza)
    if cociente.mejor_solo is not None and cociente.mejor_solo[1] > cociente.valor:
        v, valor_v = cociente.mejor_solo
        return ResultadoCostos([v], valor_v, costos[v], cociente.evaluaciones, origen="mejor_nodo_solo")
    cociente.origen = "cociente"
    return cociente


def enumeracion_parcial(oraculo, V, costos, L):
    """Enumeración parcial (Sviridenko, 2004): garantía 1 − 1/e con restricción de mochila.

    Evalúa f en todos los subconjuntos factibles de tamaño ≤ 2 y, desde cada subconjunto factible T
    de tamaño 3, completa con el voraz por cociente. Devuelve el mejor como ResultadoCostos
    (`origen` = "enumerado" o "completado"); en empate gana el primero que se encontró.
    Complejidad: evaluaciones = 1 + F₁ + F₂ + Σ_{T factible, |T| = 3} (1 + evaluaciones del voraz desde T),
    con F_j = subconjuntos factibles de tamaño j (F₁ ≤ N, F₂ ≤ C(N, 2), F₃ ≤ C(N, 3)). Cada completación
    hace O(N · mín(N, L/c_mín)) evaluaciones, así que el total es O(N⁴ · mín(N, L/c_mín)) ⊆ O(N⁵).
    Peor caso (L ≥ Σ c): 1 + N + C(N, 2) + C(N, 3)·(1 + (N − 3)(N − 2)/2) evaluaciones, Θ(N⁵).
    Mejor caso (L < c_mín): 1 evaluación y Θ(N) tiempo, porque solo se combinan los nodos que caben solos.
    Espacio O(N) más el estado del oráculo.
    """
    caben = [v for v in V if costos[v] <= L]     # un nodo que no cabe solo no está en ningún factible
    mejor = ResultadoCostos([], oraculo.valor([]), 0, 1, origen="enumerado")

    for tamano in range(1, TAMANO_ENUMERADO):    # tamaños 1 y 2: se evalúan tal cual
        for T in combinations(caben, tamano):    # orden lexicográfico de ids
            costo_T = sum(costos[v] for v in T)
            if costo_T > L:
                continue
            valor = oraculo.valor(list(T))
            mejor.evaluaciones += 1
            if valor > mejor.valor:
                mejor.S, mejor.valor, mejor.costo = list(T), valor, costo_T

    for T in combinations(caben, TAMANO_ENUMERADO):   # tamaño 3: cada uno se completa con el voraz
        if sum(costos[v] for v in T) > L:
            continue
        completado = voraz_por_cociente(oraculo, V, costos, L, inicial=T)
        mejor.evaluaciones += completado.evaluaciones
        if completado.valor > mejor.valor:
            mejor.S, mejor.valor, mejor.costo = completado.S, completado.valor, completado.costo
            mejor.origen = "completado"
    return mejor
