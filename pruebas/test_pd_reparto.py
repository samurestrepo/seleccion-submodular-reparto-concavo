"""Pruebas de red/pd_reparto.py: la PD iguala al voraz con u cóncava, lo supera con u convexa y cuenta N·(B+1)(B+2)/2."""

import math
import random
from pathlib import Path

import pytest

from red.entrada import leer_instancia
from red.pd_reparto import repartir_pd
from red.reparto import repartir_presupuesto
from red.utilidades import UtilidadLog, UtilidadRaiz, UtilidadTabla

RAIZ = Path(__file__).resolve().parent.parent
CASOS = sorted((RAIZ / "casos" / "propios").glob("*.json")) + sorted((RAIZ / "casos" / "profesora").glob("*.json"))


def _utilidad_total(x, u):
    return sum(u[i].valor(t) for i, t in x.items())


def _iguales(a, b):
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


# ---- Coincide con el voraz cuando todas las u son cóncavas ----

@pytest.mark.parametrize("ruta", CASOS, ids=lambda r: r.name)
def test_pd_iguala_al_voraz_en_los_casos_propios(ruta):
    # La PD cuesta Θ(N·B²): se usan los k primeros nodos (con el B completo) y, si es barato, todos.
    inst = leer_instancia(ruta)
    u, topes, ids = inst.utilidades(), inst.topes(), inst.ids()
    subconjuntos = [ids[:inst.k]]
    if len(ids) * (inst.B + 1) ** 2 <= 200_000:
        subconjuntos.append(ids)
    for S in subconjuntos:
        voraz = repartir_presupuesto(S, inst.B, u, topes=topes)
        pd = repartir_pd(S, inst.B, u, topes=topes)
        assert _iguales(pd.utilidad, voraz.utilidad)
        assert _iguales(_utilidad_total(pd.x, u), pd.utilidad)
        assert sum(pd.x.values()) <= inst.B
        assert all(pd.x[i] <= topes.get(i, inst.B) for i in S)


def test_pd_iguala_al_voraz_en_200_instancias_aleatorias():
    azar = random.Random(7)
    con_tope_activo = 0
    for _ in range(200):
        n, B = azar.randint(1, 4), azar.randint(0, 8)
        u, topes = {}, {}
        for i in range(1, n + 1):
            familia = azar.choice(["log", "raiz", "tabla"])
            if familia == "log":
                u[i] = UtilidadLog(round(azar.uniform(1, 10), 2))
            elif familia == "raiz":
                u[i] = UtilidadRaiz(round(azar.uniform(1, 10), 2))
            else:   # tabla cóncava: ganancias que no aumentan
                u[i] = UtilidadTabla(sorted((round(azar.uniform(0, 9), 1) for _ in range(azar.randint(1, 6))), reverse=True))
            if azar.random() < 0.5:
                topes[i] = azar.randint(0, 5)
        S = list(u)
        voraz = repartir_presupuesto(S, B, u, topes=topes)
        pd = repartir_pd(S, B, u, topes=topes)
        assert _iguales(pd.utilidad, voraz.utilidad)
        assert _iguales(_utilidad_total(pd.x, u), pd.utilidad)
        assert all(pd.x[i] <= c for i, c in topes.items()) and sum(pd.x.values()) <= B
        if sum(topes.get(i, B) for i in S) < B:
            con_tope_activo += 1
    assert con_tope_activo > 0   # se probó el caso Σ c_i < B (sobra presupuesto)


# ---- Con u convexa la PD gana ----

def test_pd_supera_al_voraz_con_utilidad_convexa():
    # u_1: 0, 5, 7 (cóncava); u_2: 0, 1, 10 (convexa). Voraz: 5 + 2 = 7; PD: todo a u_2 = 10.
    u = {1: UtilidadTabla([5, 2]), 2: UtilidadTabla([1, 9])}
    voraz = repartir_presupuesto([1, 2], 2, u)
    pd = repartir_pd([1, 2], 2, u)
    assert voraz.utilidad == 7
    assert pd.utilidad == 10 and pd.x == {1: 0, 2: 2}


def test_pd_resuelve_el_contraejemplo_convexo_del_informe():
    u = {1: UtilidadTabla([1, 10]), 2: UtilidadTabla([3, 0])}
    assert repartir_pd([1, 2], 2, u).utilidad == 11    # el voraz da 4


# ---- Bordes ----

def test_presupuesto_cero():
    u = {1: UtilidadLog(3.0), 2: UtilidadRaiz(2.0)}
    r = repartir_pd([1, 2], 0, u)
    assert r.x == {1: 0, 2: 0} and r.utilidad == 0 and r.candidatos == 2


def test_todos_los_topes_en_cero():
    u = {1: UtilidadLog(3.0), 2: UtilidadRaiz(2.0), 3: UtilidadLog(1.0)}
    r = repartir_pd([1, 2, 3], 6, u, topes={1: 0, 2: 0, 3: 0})
    assert r.x == {1: 0, 2: 0, 3: 0} and r.utilidad == 0
    assert r.candidatos == 3 * (6 + 1)          # mejor caso: N·(B + 1)


def test_un_solo_nodo_recibe_todo_hasta_su_tope():
    u = {7: UtilidadLog(4.0)}
    assert repartir_pd([7], 5, u).x == {7: 5}
    assert repartir_pd([7], 5, u, topes={7: 3}).x == {7: 3}


def test_sin_nodos_y_con_presupuesto_falla_y_sin_presupuesto_no():
    with pytest.raises(ValueError):
        repartir_pd([], 3, {})
    r = repartir_pd([], 0, {})
    assert r.x == {} and r.utilidad == 0


def test_ante_empate_gana_el_menor_t():
    u = {1: UtilidadTabla([0, 0, 0])}               # u ≡ 0: todo t empata
    assert repartir_pd([1], 3, u).x == {1: 0}


def test_ids_de_texto_y_orden_de_S():
    u = {"a": UtilidadTabla([5, 1]), "b": UtilidadTabla([4, 3])}
    r = repartir_pd(["b", "a"], 3, u)
    assert r.x == {"a": 1, "b": 2} and r.utilidad == 5 + 4 + 3


# ---- El contador ----

@pytest.mark.parametrize("N,B,exceso", [(1, 0, 0), (3, 4, 0), (5, 7, 0), (4, 6, 3)])
def test_contador_exacto_con_topes_al_menos_B(N, B, exceso):
    u = {i: UtilidadLog(1.0 + i) for i in range(1, N + 1)}
    sin_topes = repartir_pd(list(u), B, u)
    con_topes = repartir_pd(list(u), B, u, topes={i: B + exceso for i in u})
    esperado = N * (B + 1) * (B + 2) // 2
    assert sin_topes.candidatos == con_topes.candidatos == esperado


def test_contador_con_topes_intermedios_sigue_la_formula():
    u = {1: UtilidadLog(2.0), 2: UtilidadLog(3.0)}
    B, topes = 5, {1: 2, 2: 0}
    esperado = sum(min(topes[i], b) + 1 for i in u for b in range(B + 1))
    assert repartir_pd([1, 2], B, u, topes=topes).candidatos == esperado
