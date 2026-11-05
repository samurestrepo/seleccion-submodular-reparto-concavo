"""Pruebas de influencia.py: la fórmula de Δ, monotonía y submodularidad por fuerza bruta, y cobertura como caso particular."""

import math
import random
from itertools import chain, combinations

import pytest

from red.cobertura import OraculoCobertura
from red.influencia import OraculoInfluencia
from red.seleccion import seleccionar_nodos

# Ejemplo de 4 nodos: un camino A-B-C-D más la arista A-C. D y A no son vecinos (p = 0).
COEFICIENTES = {"A": 2.0, "B": 3.0, "C": 5.0, "D": 7.0}
ARISTAS = [("A", "B", 0.5), ("B", "C", 0.25), ("C", "D", 0.8), ("A", "C", 0.1)]
TOLERANCIA = 1e-9


def grafo(coeficientes, aristas):
    """id → {vecino: peso}, con cada arista en sus dos puntas."""
    vecinos = {w: {} for w in coeficientes}
    for u, v, peso in aristas:
        vecinos[u][v] = peso
        vecinos[v][u] = peso
    return vecinos


def oraculo_ejemplo():
    return OraculoInfluencia(COEFICIENTES, grafo(COEFICIENTES, ARISTAS))


def todos_los_subconjuntos(ids):
    """Todos los S ⊆ ids, cada uno como lista."""
    ids = sorted(ids)
    return [list(S) for S in chain.from_iterable(combinations(ids, n) for n in range(len(ids) + 1))]


def estado_de(oraculo, S):
    """El estado de un equipo S, construido entrando sus nodos uno por uno."""
    estado = oraculo.estado_inicial()
    for v in S:
        oraculo.agregar(estado, v)
    return estado


def formula_directa(S, coeficientes, vecinos):
    """f(S) escrita tal cual la decisión 24, sin usar nada del oráculo."""
    total = 0.0
    for w, a_w in coeficientes.items():
        q_w = 1.0
        for v in S:
            p_vw = 1.0 if v == w else vecinos[v].get(w, 0.0)
            q_w *= 1 - p_vw
        total += a_w * (1 - q_w)
    return total


def test_f_del_vacio_es_cero():
    assert oraculo_ejemplo().valor([]) == 0


def test_valor_a_mano():
    f = oraculo_ejemplo()
    # f({A}) = 2·1 + 3·0.5 + 5·0.1 = 4
    assert f.valor(["A"]) == pytest.approx(4.0)
    # f({A, C}): q_A = 0, q_C = 0, q_B = 0.5·0.75 = 0.375, q_D = 0.2 ⇒ 2 + 5 + 3·0.625 + 7·0.8 = 14.475
    assert f.valor(["A", "C"]) == pytest.approx(14.475)
    assert f.llamadas_valor == 2
    assert f.llamadas_ganancia == 0


def test_valor_coincide_con_la_formula_de_la_decision_24():
    f = oraculo_ejemplo()
    for S in todos_los_subconjuntos(COEFICIENTES):
        assert f.valor(S) == pytest.approx(formula_directa(S, COEFICIENTES, f.vecinos))


def test_ganancia_es_la_resta_de_valores_para_todo_S_y_v():
    f = oraculo_ejemplo()
    for S in todos_los_subconjuntos(COEFICIENTES):
        q = estado_de(f, S)
        for v in sorted(set(COEFICIENTES) - set(S)):
            assert f.ganancia(v, q) == pytest.approx(f.valor(S + [v]) - f.valor(S))


def test_monotona_por_fuerza_bruta():
    f = oraculo_ejemplo()
    for S in todos_los_subconjuntos(COEFICIENTES):
        for v in sorted(set(COEFICIENTES) - set(S)):
            assert f.valor(S + [v]) >= f.valor(S) - TOLERANCIA


def test_submodular_por_fuerza_bruta():
    # Si A ⊆ B y v ∉ B, entonces Δ(v | A) ≥ Δ(v | B)
    f = oraculo_ejemplo()
    comparaciones = 0
    for B in todos_los_subconjuntos(COEFICIENTES):
        for A in todos_los_subconjuntos(B):
            for v in sorted(set(COEFICIENTES) - set(B)):
                assert f.ganancia(v, estado_de(f, A)) >= f.ganancia(v, estado_de(f, B)) - TOLERANCIA
                comparaciones += 1
    assert comparaciones > 0


@pytest.mark.parametrize("pesos", [
    [("A", "B", 0), ("B", "C", 1), ("C", "D", 1), ("A", "C", 0)],
    [("A", "B", 1), ("B", "C", 0), ("C", "D", 1), ("A", "D", 0)],
    [("A", "B", 1), ("A", "C", 1), ("A", "D", 1), ("B", "C", 1)],
    [],
])
def test_con_pesos_0_y_1_da_lo_mismo_que_cobertura(pesos):
    # Con a_w = 1, C_v = {v} ∪ {w : p_vw = 1} y f(S) es el tamaño de la unión
    unos = {w: 1.0 for w in COEFICIENTES}
    vecinos = grafo(unos, pesos)
    conjuntos = {v: frozenset({v} | {w for w, p in vecinos[v].items() if p == 1}) for v in unos}
    influencia = OraculoInfluencia(unos, vecinos)
    cobertura = OraculoCobertura(conjuntos)
    for S in todos_los_subconjuntos(unos):
        assert influencia.valor(S) == pytest.approx(cobertura.valor(S))
    V = sorted(unos)
    S_influencia, valor_influencia = seleccionar_nodos(OraculoInfluencia(unos, vecinos), V, 2)
    S_cobertura, valor_cobertura = seleccionar_nodos(OraculoCobertura(conjuntos), V, 2)
    assert S_influencia == S_cobertura
    assert valor_influencia == pytest.approx(valor_cobertura)


def test_estado_inicial_es_nuevo_y_vale_uno():
    f = oraculo_ejemplo()
    q = f.estado_inicial()
    assert q == {"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0}
    assert f.estado_inicial() is not q


def test_agregar_actualiza_en_su_lugar_y_no_cuenta():
    f = oraculo_ejemplo()
    q = f.estado_inicial()
    assert f.agregar(q, "A") is q
    assert q == {"A": 0.0, "B": 0.5, "C": 0.9, "D": 1.0}
    assert f.llamadas_ganancia == 0
    assert f.llamadas_valor == 0


def test_ganancia_cuenta_una_llamada_y_no_toca_el_estado():
    f = oraculo_ejemplo()
    q = f.estado_inicial()
    antes = dict(q)
    f.ganancia("B", q)
    assert q == antes
    assert f.llamadas_ganancia == 1


class EstadoContado(dict):
    """Un estado que cuenta cuántas posiciones se leen o se escriben."""

    def __init__(self, datos):
        super().__init__(datos)
        self.accesos = 0

    def __getitem__(self, clave):
        self.accesos += 1
        return super().__getitem__(clave)

    def __setitem__(self, clave, valor):
        self.accesos += 1
        super().__setitem__(clave, valor)


@pytest.mark.parametrize("grado", [0, 1, 5, 40])
def test_costo_de_ganancia_y_agregar_depende_solo_del_grado(grado):
    # Sin reloj: 200 nodos, pero solo se tocan v y sus vecinos
    coeficientes = {i: 1.0 for i in range(200)}
    vecinos = grafo(coeficientes, [(0, w, 0.5) for w in range(1, grado + 1)])
    f = OraculoInfluencia(coeficientes, vecinos)

    q = EstadoContado(f.estado_inicial())
    f.ganancia(0, q)
    assert q.accesos == 1 + grado

    q = EstadoContado(f.estado_inicial())
    f.agregar(q, 0)
    assert q.accesos == 1 + 2 * grado   # q_v se escribe; cada q_w se lee y se escribe


def instancia_al_azar(generador, n):
    """Coeficientes y grafo pequeños, con pesos en [0, 1] y algunas aristas ausentes."""
    coeficientes = {i: generador.uniform(0.5, 12.0) for i in range(n)}
    aristas = [(u, v, generador.random()) for u, v in combinations(range(n), 2)
               if generador.random() < 0.7]
    return coeficientes, grafo(coeficientes, aristas)


def test_el_voraz_respeta_la_cota_y_el_conteo_de_llamadas():
    generador = random.Random(7)
    for _ in range(150):
        n = generador.randint(2, 8)
        k = generador.randint(1, n - 1)
        coeficientes, vecinos = instancia_al_azar(generador, n)
        f = OraculoInfluencia(coeficientes, vecinos)
        S, valorS = seleccionar_nodos(f, sorted(coeficientes), k)
        assert f.llamadas_ganancia == k * n - k * (k - 1) // 2
        # El valor acumulado con el estado coincide con f(S) calculada desde cero
        assert valorS == pytest.approx(f.valor(S))
        optimo = max(f.valor(list(T)) for T in combinations(sorted(coeficientes), k))
        assert valorS >= (1 - 1 / math.e) * optimo - TOLERANCIA
