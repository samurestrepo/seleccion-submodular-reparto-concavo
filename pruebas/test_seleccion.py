import math
import random
import tracemalloc

import pytest

from pruebas.fuerza_bruta import mejor_seleccion
from red.cobertura import OraculoCobertura
from red.seleccion import seleccionar_nodos
from red.traza import Traza


def correr(conjuntos, k, traza=None):
    f = OraculoCobertura(conjuntos)
    S, valor = seleccionar_nodos(f, sorted(conjuntos), k, traza)
    return S, valor, f


def test_ejemplo_del_informe():
    # Sección 6.3: elige 1 y luego 3, con 5 letras
    traza = Traza()
    S, valor, _ = correr({1: frozenset("abc"), 2: frozenset("cd"), 3: frozenset("de")}, 2, traza)
    assert S == [1, 3]
    assert valor == 5
    assert [a["ganancia"] for a in traza.pasos_seleccion[0]["aportes"]] == [3, 2, 2]
    assert [a["ganancia"] for a in traza.pasos_seleccion[1]["aportes"]] == [1, 2]


def test_contraejemplo_el_voraz_no_es_exacto():
    # El voraz toma {1,2,3,4} primero y llega a 5; el óptimo {2, 3} cubre 6
    conjuntos = {1: frozenset({1, 2, 3, 4}), 2: frozenset({1, 2, 5}), 3: frozenset({3, 4, 6})}
    S, valor, _ = correr(conjuntos, 2)
    assert S == [1, 2]
    assert valor == 5
    assert mejor_seleccion(conjuntos, 2) == 6


def test_empate_gana_el_menor_indice():
    S, _, _ = correr({1: frozenset("a"), 2: frozenset("b"), 3: frozenset("c")}, 2)
    assert S == [1, 2]


def test_sin_traza_no_se_guardan_los_aportes():
    # H4: sin traza el espacio es O(k + |U|); antes se guardaba una pareja (v, Δ) por candidato
    N = 20000
    conjuntos = {i: frozenset() for i in range(N)}
    conjuntos[0] = frozenset("a")
    V = sorted(conjuntos)
    f = OraculoCobertura(conjuntos)
    tracemalloc.start()
    try:
        seleccionar_nodos(f, V, 1)
        _, pico = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    # Las parejas ocupaban unos 72 bytes por candidato (1.4 MB en total); sin ellas casi nada
    assert pico < 100_000


def test_con_traza_si_se_guardan_los_aportes():
    traza = Traza()
    correr({1: frozenset("a"), 2: frozenset("b"), 3: frozenset("c")}, 1, traza)
    assert [a["nodo"] for a in traza.pasos_seleccion[0]["aportes"]] == [1, 2, 3]


@pytest.mark.parametrize("N, k", [(3, 1), (3, 2), (10, 4), (25, 7)])
def test_cuenta_exacta_de_llamadas(N, k):
    conjuntos = {i: frozenset({i}) for i in range(1, N + 1)}
    _, _, f = correr(conjuntos, k)
    assert f.llamadas_ganancia == k * N - k * (k - 1) // 2


def test_respeta_la_cota_1_menos_1_sobre_e():
    azar = random.Random(7)
    for _ in range(200):
        N = azar.randint(3, 8)
        k = azar.randint(1, N - 1)
        conjuntos = {i: frozenset(azar.sample(range(10), azar.randint(1, 5))) for i in range(1, N + 1)}
        _, valor, _ = correr(conjuntos, k)
        assert valor >= (1 - 1 / math.e) * mejor_seleccion(conjuntos, k)
