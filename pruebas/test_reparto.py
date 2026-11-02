import math
import random

import pytest

from pruebas.fuerza_bruta import mejor_reparto
from red.reparto import repartir_presupuesto
from red.traza import Traza
from red.utilidades import UtilidadLog, UtilidadRaiz, UtilidadTabla


def test_ejemplo_del_informe():
    # Sección 6.4: P = 9, 5, 2, 1 y Q = 7, 6, 1, 0 con B = 4 da 27 (P, Q, Q, P)
    u = {1: UtilidadTabla([9, 5, 2, 1]), 2: UtilidadTabla([7, 6, 1, 0])}
    traza = Traza()
    r = repartir_presupuesto([1, 2], 4, u, traza)
    assert r.x == {1: 2, 2: 2}
    assert r.utilidad == 27
    assert [p["nodo"] for p in traza.unidades_reparto] == [1, 2, 2, 1]
    assert [p["ganancia"] for p in traza.unidades_reparto] == [9, 7, 6, 5]


def test_contraejemplo_convexo():
    # P = 1, 10 no es cóncava: el voraz da 4 y el óptimo (todo a P) es 11
    u = {1: UtilidadTabla([1, 10]), 2: UtilidadTabla([3, 0])}
    r = repartir_presupuesto([1, 2], 2, u)
    assert r.utilidad == 4
    assert mejor_reparto([1, 2], 2, u) == 11


def test_empate_gana_el_menor_indice():
    u = {1: UtilidadTabla([5, 5]), 2: UtilidadTabla([5, 5])}
    traza = Traza()
    repartir_presupuesto([2, 1], 1, u, traza)
    assert traza.unidades_reparto[0]["nodo"] == 1


def test_presupuesto_cero():
    r = repartir_presupuesto([1, 2], 0, {1: UtilidadLog(1), 2: UtilidadLog(2)})
    assert r.x == {1: 0, 2: 0}
    assert r.utilidad == 0
    assert r.extracciones == r.inserciones == 0


def test_sin_nodos_y_con_presupuesto_falla():
    with pytest.raises(ValueError):
        repartir_presupuesto([], 3, {})


def test_contadores_valen_B():
    u = {i: UtilidadRaiz(i) for i in range(1, 6)}
    r = repartir_presupuesto(list(u), 37, u)
    assert r.extracciones == r.inserciones == 37
    assert sum(r.x.values()) == 37


def test_coincide_con_fuerza_bruta():
    azar = random.Random(3)
    for _ in range(150):
        n = azar.randint(1, 4)
        B = azar.randint(0, 8)
        u = {}
        for i in range(1, n + 1):
            familia = azar.choice([UtilidadLog, UtilidadRaiz])
            u[i] = familia(round(azar.uniform(1, 10), 2))
        r = repartir_presupuesto(list(u), B, u)
        assert math.isclose(r.utilidad, mejor_reparto(list(u), B, u), rel_tol=1e-9, abs_tol=1e-9)
