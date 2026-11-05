import math
import random

import pytest

from pruebas.fuerza_bruta import mejor_reparto, mejor_reparto_con_topes
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


# ---- Topes por nodo (x_i ≤ c_i) ----

def test_tope_2_con_B_3_deja_de_insertar_al_que_llega():
    # Receta 3: el nodo 1 domina, llega a su tope y no vuelve al montículo
    u = {1: UtilidadLog(10), 2: UtilidadLog(1)}
    r = repartir_presupuesto([1, 2], 3, u, topes={1: 2})
    assert r.x == {1: 2, 2: 1}
    assert r.extracciones == 3
    assert r.inserciones == 2


def test_tope_cambia_el_reparto_del_caso_activo():
    u = {1: UtilidadLog(10), 2: UtilidadLog(1)}
    assert repartir_presupuesto([1, 2], 5, u).x == {1: 5, 2: 0}
    r = repartir_presupuesto([1, 2], 5, u, topes={1: 2})
    assert r.x == {1: 2, 2: 3}
    assert (r.extracciones, r.inserciones) == (5, 4)


def test_topes_que_no_alcanzan_dejan_presupuesto_sin_gastar():
    # Σ c_i = 2 < B = 9: el ciclo para cuando el montículo se vacía, sin error
    u = {1: UtilidadLog(1), 2: UtilidadLog(5)}
    traza = Traza()
    r = repartir_presupuesto([1, 2], 9, u, traza, topes={1: 2, 2: 0})
    assert r.x == {1: 2, 2: 0}
    assert r.extracciones == 2
    assert r.inserciones == 1
    assert len(traza.unidades_reparto) == 2
    assert r.utilidad == pytest.approx(u[1].valor(2))


def test_todos_con_tope_cero_no_reciben_nada():
    u = {1: UtilidadLog(1), 2: UtilidadLog(5)}
    r = repartir_presupuesto([1, 2], 4, u, topes={1: 0, 2: 0})
    assert r.x == {1: 0, 2: 0}
    assert r.utilidad == 0
    assert (r.extracciones, r.inserciones) == (0, 0)


def test_tope_exacto_en_la_ultima_unidad_no_inserta():
    u = {1: UtilidadLog(10), 2: UtilidadLog(1)}
    r = repartir_presupuesto([1, 2], 2, u, topes={1: 2})
    assert r.x == {1: 2, 2: 0}
    assert (r.extracciones, r.inserciones) == (2, 1)


def test_tope_mayor_que_B_no_cambia_nada():
    u = {1: UtilidadLog(3), 2: UtilidadRaiz(2)}
    con_tope = repartir_presupuesto([1, 2], 6, u, topes={1: 100, 2: 100})
    sin_tope = repartir_presupuesto([1, 2], 6, u)
    assert con_tope.x == sin_tope.x
    assert con_tope.utilidad == sin_tope.utilidad
    assert (con_tope.extracciones, con_tope.inserciones) == (6, 6)


def test_topes_con_ids_de_texto():
    u = {"N01": UtilidadLog(10), "N02": UtilidadLog(1)}
    r = repartir_presupuesto(["N01", "N02"], 5, u, topes={"N01": 2})
    assert r.x == {"N01": 2, "N02": 3}


def test_el_que_llega_a_su_tope_no_gana_el_empate_despues():
    # Empate por el menor índice: el nodo 1 sale primero hasta su tope y luego sigue el 2
    u = {1: UtilidadTabla([5, 5, 5]), 2: UtilidadTabla([5, 5, 5])}
    traza = Traza()
    repartir_presupuesto([1, 2], 3, u, traza, topes={1: 1})
    assert [p["nodo"] for p in traza.unidades_reparto] == [1, 2, 2]


def test_con_topes_coincide_con_fuerza_bruta():
    azar = random.Random(5)
    activos = 0
    for _ in range(300):
        n = azar.randint(1, 4)
        B = azar.randint(0, 8)
        u = {}
        topes = {}
        for i in range(1, n + 1):
            familia = azar.choice([UtilidadLog, UtilidadRaiz])
            u[i] = familia(round(azar.uniform(1, 10), 2))
            if azar.random() < 0.7:
                topes[i] = azar.randint(0, 4)
        r = repartir_presupuesto(list(u), B, u, topes=topes)
        esperado = mejor_reparto_con_topes(list(u), B, u, topes)
        assert math.isclose(r.utilidad, esperado, rel_tol=1e-9, abs_tol=1e-9)
        assert all(r.x[i] <= c for i, c in topes.items())
        if r.utilidad < mejor_reparto(list(u), B, u) - 1e-9:
            activos += 1
    assert activos > 0   # si ningún tope limitara, esta prueba no comprobaría nada
