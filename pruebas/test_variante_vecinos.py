"""Variante (c): vecinos que alteran la utilidad (red/variante_vecinos.py). Reducción a la base con β = 0,
c1 = exacto, contraejemplo mínimo de c2, cota 1 − (1 − 1/B)^B en la batería, rendimientos decrecientes,
ganancias que cambian (distancia ≤ 2), conteos, enumeración, rechazos, ejecutar.py y las evidencias."""

import csv
import json
import math
import random
import sys
from math import comb
from pathlib import Path

import pytest

from ejecutar import ENCABEZADO, main
from red.entrada import instancia_desde_diccionario, leer_instancia
from red.generador import generar_instancia_influencia
from red.reparto import repartir_presupuesto
from red.ronda import ejecutar_ronda
from red.seleccion import seleccionar_nodos
from red.variante_vecinos import (BETA, LIMITE_REPARTOS, DemasiadosRepartos, ResultadoVecinos, _afectados,
                                  a_texto_vecinos, coeficientes_c1, contar_repartos, cota_c2, ejecutar_variante_c,
                                  ganancia_c2, repartir_c1, repartir_c2, repartir_exacto, utilidad_c1,
                                  utilidad_c2, vecinos_en_S)
from red.verificacion import verificar_reparto_c2, verificar_reparto_contra_exacto, verificar_variante_c

RAIZ = Path(__file__).resolve().parent.parent
PROFESORA = RAIZ / "casos" / "profesora" / "entrada_G2_red_15_nodos.json"
EVIDENCIAS = RAIZ / "resultados" / "variantes"
REPARTOS_PROFESORA = 302792   # C(35, 5) − 5·C(16, 5): |S| = 5, B = 30, topes 18

sys.path.insert(0, str(RAIZ / "scripts"))
import tabla_cota_variante_c  # noqa: E402


def _grafo(nodos, aristas):
    """id → {vecino: peso} a partir de una lista de (u, v, w)."""
    vecinos = {i: {} for i in nodos}
    for u, v, w in aristas:
        vecinos[u][v] = w
        vecinos[v][u] = w
    return vecinos


def _instancias_con_grafo():
    """La docente y 6 instancias de influencia del generador (con su S del voraz base)."""
    instancias = [leer_instancia(PROFESORA)]
    for n, densidad, semilla in ((8, 0.3, 1), (8, 1.0, 2), (10, 0.6, 3), (12, 0.3, 2), (12, 1.0, 1), (10, 1.0, 1)):
        datos = generar_instancia_influencia(n, 4, 12, densidad, semilla)
        instancias.append(instancia_desde_diccionario(datos, f"N{n}_d{densidad}_s{semilla}"))
    return instancias


def _S_y_coeficientes(inst):
    S, _ = seleccionar_nodos(inst.crear_oraculo(), inst.ids(), inst.k)
    return S, {nodo.id: nodo.utilidad.a for nodo in inst.nodos}


# ---------------------------------------------------------------- β = 0 reproduce la base

@pytest.mark.parametrize("inst", _instancias_con_grafo(), ids=lambda i: i.nombre)
def test_con_beta_cero_c1_y_c2_dan_el_reparto_base(inst):
    S, coef = _S_y_coeficientes(inst)
    base = repartir_presupuesto(S, inst.B, inst.utilidades(), topes=inst.topes())
    c1, a_prima = repartir_c1(S, inst.B, coef, inst.vecinos, 0.0, inst.topes())
    c2 = repartir_c2(S, inst.B, coef, inst.vecinos, 0.0, inst.topes())
    assert a_prima == {i: coef[i] for i in S}
    assert c1.x == base.x and c2.x == base.x
    assert math.isclose(c1.utilidad, base.utilidad, rel_tol=1e-12)
    assert math.isclose(c2.utilidad, base.utilidad, rel_tol=1e-12)


@pytest.mark.parametrize("modelo", ["c1", "c2"])
def test_con_beta_cero_la_ronda_de_la_variante_es_la_de_la_base(modelo):
    inst = leer_instancia(PROFESORA)
    base = ejecutar_ronda(inst, 1)
    r = ejecutar_variante_c(inst, modelo, 0.0, 1, limite=0)   # límite 0: sin enumeración, para que sea rápida
    assert r["todas_cumplen"]
    assert r["seleccion"]["S"] == base["seleccion"]["S"] and r["seleccion"]["valor"] == base["seleccion"]["valor"]
    assert r["reparto"]["x"] == base["reparto"]["x"]
    assert math.isclose(r["reparto"]["utilidad"], base["reparto"]["utilidad"], rel_tol=1e-12)
    assert r["exacto"]["disponible"] is False and r["exacto"]["repartos"] == REPARTOS_PROFESORA


# ---------------------------------------------------------------- c1

def test_c1_reagrupa_los_coeficientes():
    vecinos = _grafo([1, 2, 3, 4], [(1, 2, 0.5), (2, 3, 0.25), (3, 4, 1.0)])
    S = [1, 2, 3]   # el 4 no está en S: su arista con 3 no cuenta (Supuesto ❓)
    a = coeficientes_c1(S, {1: 1.0, 2: 2.0, 3: 3.0, 4: 9.0}, vecinos_en_S(S, vecinos), 0.2)
    assert a == pytest.approx({1: 1.0 + 0.2 * 0.5, 2: 2.0 + 0.2 * 0.75, 3: 3.0 + 0.2 * 0.25})


def test_c1_es_la_suma_de_los_dos_efectos():
    """U de c1 = Σ_j [a_j·ln(1 + x_j) + Σ_{i vecino de j} β·w_ij·ln(1 + x_i)] (la definición sin reagrupar)."""
    vecinos = _grafo([1, 2, 3], [(1, 2, 0.5), (2, 3, 0.3)])
    coef = {1: 2.0, 2: 3.0, 3: 1.5}
    x = {1: 2, 2: 1, 3: 4}
    a_prima = coeficientes_c1([1, 2, 3], coef, vecinos_en_S([1, 2, 3], vecinos), 0.2)
    directo = sum(coef[j] * math.log(1 + x[j]) + sum(0.2 * w * math.log(1 + x[i]) for i, w in vecinos[j].items())
                  for j in x)
    assert math.isclose(utilidad_c1(x, a_prima), directo, rel_tol=1e-12)


def test_c1_coincide_con_la_enumeracion_en_el_contraejemplo_de_c2():
    vecinos = _grafo([1, 2, 3], [(1, 2, 1.0), (2, 3, 1.0)])
    coef = {1: 3.0, 2: 2.0, 3: 3.0}
    r, a_prima = repartir_c1([1, 2, 3], 2, coef, vecinos, 0.2)
    _, opt, _ = repartir_exacto([1, 2, 3], 2, lambda x: utilidad_c1(x, a_prima))
    assert math.isclose(r.utilidad, opt, rel_tol=1e-12)


# ---------------------------------------------------------------- c2: contraejemplo mínimo

def test_contraejemplo_minimo_de_c2():
    """Trayecto 1 – 2 – 3, a = (3, 2, 3), w = 1, β = 0,2, B = 2. La primera unidad va al centro (le sube a
    los dos extremos); la segunda, al nodo 1. El óptimo le da una a cada extremo."""
    vecinos = _grafo([1, 2, 3], [(1, 2, 1.0), (2, 3, 1.0)])
    coef = {1: 3.0, 2: 2.0, 3: 3.0}
    voraz = repartir_c2([1, 2, 3], 2, coef, vecinos, 0.2)
    x_opt, opt, evaluados = repartir_exacto([1, 2, 3], 2,
                                            lambda x: utilidad_c2(x, coef, vecinos_en_S([1, 2, 3], vecinos), 0.2))
    assert voraz.x == {1: 1, 2: 1, 3: 0}
    assert math.isclose(voraz.utilidad, 5 * math.log(2.2) + 3 * math.log(1.2))        # ≈ 4,489251
    assert x_opt == {1: 1, 2: 0, 3: 1}
    assert math.isclose(opt, 6 * math.log(2) + 2 * math.log(1.4))                       # ≈ 4,831828
    assert voraz.utilidad < opt
    assert round(voraz.utilidad / opt, 6) == 0.929100
    assert voraz.utilidad / opt >= cota_c2(2) == 0.75
    assert evaluados == comb(2 + 3, 3) == 10


def test_la_primera_unidad_del_contraejemplo_va_al_centro():
    vecinos = vecinos_en_S([1, 2, 3], _grafo([1, 2, 3], [(1, 2, 1.0), (2, 3, 1.0)]))
    coef = {1: 3.0, 2: 2.0, 3: 3.0}
    z = {1: 0.0, 2: 0.0, 3: 0.0}
    extremo, centro = ganancia_c2(1, z, coef, vecinos, 0.2), ganancia_c2(2, z, coef, vecinos, 0.2)
    assert math.isclose(extremo, 3 * math.log(2) + 2 * math.log(1.2))
    assert math.isclose(centro, 2 * math.log(2) + 6 * math.log(1.2))
    assert centro > extremo


# ---------------------------------------------------------------- c2: por qué la cota

def _instancia_aleatoria(azar, n=4):
    nodos = list(range(1, n + 1))
    aristas = [(i, j, round(azar.uniform(0.05, 1.0), 2)) for i in nodos for j in nodos if i < j and azar.random() < 0.6]
    return nodos, _grafo(nodos, aristas), {i: round(azar.uniform(1, 10), 2) for i in nodos}


@pytest.mark.parametrize("semilla", range(20))
def test_U_de_c2_es_monotona_y_con_rendimientos_decrecientes(semilla):
    """Punto 1 de la cota: U(0) = 0, Δ_i > 0 y Δ_i(x + e_l) ≤ Δ_i(x) para todo i, l (incluido l = i)."""
    azar = random.Random(semilla)
    S, vecinos, coef = _instancia_aleatoria(azar)
    grafo_S = vecinos_en_S(S, vecinos)
    beta = azar.choice([0.2, 1.0, 3.0])
    assert utilidad_c2({i: 0 for i in S}, coef, grafo_S, beta) == 0

    def delta(x, i):
        y = dict(x)
        y[i] += 1
        return utilidad_c2(y, coef, grafo_S, beta) - utilidad_c2(x, coef, grafo_S, beta)

    for _ in range(15):
        x = {i: azar.randint(0, 4) for i in S}
        for i in S:
            assert delta(x, i) > 0
            for l in S:
                y = dict(x)
                y[l] += 1
                assert delta(y, i) <= delta(x, i) + 1e-12


@pytest.mark.parametrize("semilla", range(30))
def test_c2_respeta_la_cota_en_instancias_pequenas(semilla):
    azar = random.Random(100 + semilla)
    S, vecinos, coef = _instancia_aleatoria(azar)
    B, beta = azar.randint(1, 6), azar.choice([0.2, 0.5, 2.0])
    voraz = repartir_c2(S, B, coef, vecinos, beta)
    _, opt, _ = repartir_exacto(S, B, lambda x: utilidad_c2(x, coef, vecinos_en_S(S, vecinos), beta))
    assert voraz.utilidad <= opt + 1e-9
    assert voraz.utilidad >= cota_c2(B) * opt - 1e-9


def test_cota_c2():
    assert cota_c2(0) == 0.0 and cota_c2(1) == 1.0 and cota_c2(2) == 0.75
    assert cota_c2(30) > 1 - 1 / math.e


# ---------------------------------------------------------------- c2: qué ganancias cambian

def test_las_ganancias_cambian_hasta_distancia_dos():
    """En el trayecto 1 – 2 – 3, darle una unidad a 1 cambia la ganancia de 3 (a distancia 2), no solo
    la de 1 y la de su vecino 2: la ganancia de 3 incluye el término de su vecino 2, cuyo z subió."""
    grafo_S = vecinos_en_S([1, 2, 3, 4], _grafo([1, 2, 3, 4], [(1, 2, 1.0), (2, 3, 1.0), (3, 4, 1.0)]))
    coef = {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0}
    antes = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    despues = {1: 1.0, 2: 0.2, 3: 0.0, 4: 0.0}   # 1 recibió una unidad
    cambia = {l for l in grafo_S if ganancia_c2(l, antes, coef, grafo_S, 0.2) != ganancia_c2(l, despues, coef, grafo_S, 0.2)}
    assert cambia == {1, 2, 3} == _afectados(1, grafo_S)
    assert 4 not in _afectados(1, grafo_S)


def _voraz_c2_sin_atajos(S, B, coef, vecinos, beta, topes):
    """Referencia: recalcula TODAS las ganancias en cada paso desde x (sin estado z)."""
    grafo_S = vecinos_en_S(S, vecinos)
    x = {i: 0 for i in S}
    for _ in range(B):
        activos = [i for i in sorted(S) if x[i] < topes.get(i, B)]
        if not activos:
            break
        base = utilidad_c2(x, coef, grafo_S, beta)
        mejor, mejor_delta = None, None
        for i in activos:
            x[i] += 1
            d = utilidad_c2(x, coef, grafo_S, beta) - base
            x[i] -= 1
            if mejor is None or d > mejor_delta + 1e-12:
                mejor, mejor_delta = i, d
        x[mejor] += 1
    return x


@pytest.mark.parametrize("semilla", range(25))
def test_recalcular_solo_las_afectadas_da_lo_mismo_que_recalcular_todo(semilla):
    azar = random.Random(500 + semilla)
    S, vecinos, coef = _instancia_aleatoria(azar, n=azar.randint(3, 7))
    topes = {i: azar.randint(0, 4) for i in S if azar.random() < 0.4}
    B, beta = azar.randint(0, 12), azar.choice([0.2, 1.0])
    assert repartir_c2(S, B, coef, vecinos, beta, topes).x == _voraz_c2_sin_atajos(S, B, coef, vecinos, beta, topes)


def test_conteos_de_c2_con_S_completo_y_con_S_sin_aristas():
    """S completo: cada paso recalcula las |S| ganancias. Sin aristas: solo la del elegido. Barrido: |S| por paso."""
    S = [1, 2, 3, 4]
    coef = {1: 1.0, 2: 2.0, 3: 3.0, 4: 4.0}
    completo = _grafo(S, [(i, j, 0.5) for i in S for j in S if i < j])
    r = repartir_c2(S, 10, coef, completo, 0.2)
    assert (r.pasos, r.ganancias_recalculadas, r.revisados) == (10, 4 + 10 * 4, 10 * 4)
    r = repartir_c2(S, 10, coef, _grafo(S, []), 0.2)
    assert (r.pasos, r.ganancias_recalculadas, r.revisados) == (10, 4 + 10, 10 * 4)


def test_c2_respeta_los_topes_y_deja_sobrar_presupuesto():
    S = [1, 2, 3]
    vecinos = _grafo(S, [(1, 2, 0.5)])
    r = repartir_c2(S, 10, {1: 5.0, 2: 1.0, 3: 1.0}, vecinos, 0.2, topes={1: 2, 2: 0, 3: 3})
    assert r.x == {1: 2, 2: 0, 3: 3} and r.pasos == 5
    assert repartir_c2(S, 0, {1: 1.0, 2: 1.0, 3: 1.0}, vecinos, 0.2).x == {1: 0, 2: 0, 3: 0}
    with pytest.raises(ValueError):
        repartir_c2([], 3, {}, {}, 0.2)


def test_c2_desempata_por_el_menor_id():
    S = [3, 1, 2]   # el orden de S no importa: el barrido va por id
    r = repartir_c2(S, 1, {1: 2.0, 2: 2.0, 3: 2.0}, _grafo(S, []), 0.2)
    assert r.x == {3: 0, 1: 1, 2: 0}


# ---------------------------------------------------------------- enumeración

@pytest.mark.parametrize("m,B", [(1, 0), (1, 5), (3, 4), (5, 6), (4, 10)])
def test_contar_repartos_sin_topes_es_combinatorio(m, B):
    assert contar_repartos(list(range(m)), B) == comb(B + m, m)


def test_contar_repartos_de_la_docente():
    S = ["N11", "N14", "N09", "N15", "N13"]
    assert contar_repartos(S, 30, {i: 18 for i in S}) == comb(35, 5) - 5 * comb(16, 5) == REPARTOS_PROFESORA


@pytest.mark.parametrize("semilla", range(10))
def test_la_enumeracion_evalua_exactamente_los_repartos_contados(semilla):
    azar = random.Random(semilla)
    S = list(range(azar.randint(1, 4)))
    topes = {i: azar.randint(0, 5) for i in S if azar.random() < 0.5}
    B = azar.randint(0, 7)
    vistos = []
    _, _, evaluados = repartir_exacto(S, B, lambda x: vistos.append(dict(x)) or 0.0, topes)
    assert evaluados == len(vistos) == contar_repartos(S, B, topes)
    assert all(sum(x.values()) <= B and all(x[i] <= topes.get(i, B) for i in S) for x in vistos)
    assert [tuple(x[i] for i in sorted(S)) for x in vistos] == sorted(tuple(x[i] for i in sorted(S)) for x in vistos)


def test_la_enumeracion_desempata_por_el_primero_lexicografico():
    """Dos nodos iguales sin aristas y B = 1: (0, 1) va antes que (1, 0). El voraz, en cambio, elige al menor id."""
    x, _, _ = repartir_exacto([1, 2], 1, lambda x: math.log(1 + x[1]) + math.log(1 + x[2]))
    assert x == {1: 0, 2: 1}


def test_la_enumeracion_se_niega_sin_evaluar_si_hay_demasiados():
    llamadas = []
    with pytest.raises(DemasiadosRepartos, match="302792"):
        repartir_exacto(list("abcde"), 30, lambda x: llamadas.append(1) or 0.0, {i: 18 for i in "abcde"})
    assert llamadas == [] and LIMITE_REPARTOS == 200000


# ---------------------------------------------------------------- batería (scripts/tabla_cota_variante_c.py)

@pytest.fixture(scope="module")
def bateria():
    return tabla_cota_variante_c.bateria()


def test_bateria_c1_coincide_con_el_exacto_y_c2_respeta_la_cota(bateria):
    assert len(bateria) == 27 * 4 * 3
    assert all(f["c1_coincide"] for f in bateria)
    assert all(f["razon_c2"] <= 1 + 1e-9 for f in bateria)
    assert all(f["razon_c2"] >= f["cota_c2"] - 1e-9 for f in bateria)
    assert all(f["cumple"] for f in bateria)
    assert min(f["razon_c2"] for f in bateria) == 0.986703184
    assert sum(f["razon_c2"] < 1 - 1e-9 for f in bateria) == 7


def test_el_csv_del_repositorio_es_el_de_la_bateria(bateria):
    with open(EVIDENCIAS / "c_tabla_cota.csv", encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    assert list(filas[0].keys()) == tabla_cota_variante_c.COLUMNAS
    assert len(filas) == len(bateria)
    for guardada, nueva in zip(filas, bateria):
        assert guardada["caso"] == nueva["caso"] and float(guardada["beta"]) == nueva["beta"]
        assert guardada["x_c2_voraz"] == nueva["x_c2_voraz"] and float(guardada["razon_c2"]) == nueva["razon_c2"]


# ---------------------------------------------------------------- verificaciones y rechazos

def test_el_formato_propio_se_rechaza_sin_grafo():
    datos = {"k": 1, "B": 2, "nodos": [{"id": 1, "cubre": ["a"], "utilidad": {"tipo": "log", "a": 1.0}},
                                       {"id": 2, "cubre": ["b"], "utilidad": {"tipo": "raiz", "a": 1.0}}]}
    inst = instancia_desde_diccionario(datos, "propio")
    v = verificar_variante_c(inst)
    assert [x.cumple for x in v] == [False, False]
    r = ejecutar_variante_c(inst, "c2")
    assert r["todas_cumplen"] is False and "seleccion" not in r
    assert any("grafo" in m for m in r["traza"]["motivo_rechazo"])


@pytest.mark.parametrize("parametros", [{"modelo": "c3"}, {"beta": -0.1}, {"beta": float("inf")}, {"beta": True},
                                        {"repeticiones": 0}, {"limite": -1}])
def test_parametros_invalidos(parametros):
    with pytest.raises(ValueError):
        ejecutar_variante_c(leer_instancia(PROFESORA), **parametros)


def test_verificar_reparto_contra_exacto_detecta_las_fallas():
    assert verificar_reparto_contra_exacto("c1", 10.0, 10.0, 1.0)[0].cumple
    assert not verificar_reparto_contra_exacto("c1", 9.0, 10.0, 1.0)[0].cumple
    assert [v.cumple for v in verificar_reparto_contra_exacto("c2", 9.0, 10.0, 0.75)] == [True, True]
    assert [v.cumple for v in verificar_reparto_contra_exacto("c2", 7.0, 10.0, 0.75)] == [True, False]
    assert [v.cumple for v in verificar_reparto_contra_exacto("c2", 11.0, 10.0, 0.75)] == [False, True]


def test_verificar_reparto_c2_detecta_las_fallas():
    malo = ResultadoVecinos({1: 3, 2: 0}, 5.0, 2, 0, 0)
    v = verificar_reparto_c2([1, 2], 3, malo, lambda x: 5.0, topes={1: 2})
    assert [x.cumple for x in v] == [False, True, False]


# ---------------------------------------------------------------- ejecutar.py y evidencias de la docente

@pytest.mark.parametrize("modelo", ["c1", "c2"])
def test_ejecutar_con_la_variante_c(tmp_path, modelo):
    codigo = main([str(PROFESORA), "--variante", modelo, "--beta", "0.2", "--repeticiones", "1",
                   "--salida", str(tmp_path)])
    assert codigo == 0
    carpeta = tmp_path / PROFESORA.stem
    salida = json.loads((carpeta / "salida.json").read_text(encoding="utf-8"))
    assert salida["variante_c"]["modelo"] == modelo and salida["variante_c"]["beta"] == 0.2
    assert salida["exacto"]["disponible"] is False   # 302792 > 200000 con el límite por omisión
    assert "Supuesto ❓" in (carpeta / "traza.txt").read_text(encoding="utf-8")
    with open(tmp_path / "resumen.csv", encoding="utf-8") as archivo:
        assert next(csv.reader(archivo)) == ENCABEZADO


@pytest.mark.parametrize("argumentos", [["--beta", "-1"], ["--beta", "nan"], ["--beta", "x"],
                                        ["--limite-repartos", "0"]])
def test_ejecutar_rechaza_parametros_malos(tmp_path, argumentos):
    with pytest.raises(SystemExit):
        main([str(PROFESORA), "--variante", "c1", "--salida", str(tmp_path)] + argumentos)


def test_beta_por_omision():
    assert BETA == 0.2


def _evidencia(modelo):
    return json.loads((EVIDENCIAS / f"{modelo}_profesora" / PROFESORA.stem / "salida.json").read_text(encoding="utf-8"))


def test_evidencia_c1_de_la_docente():
    e = _evidencia("c1")
    assert e["todas_cumplen"] and e["seleccion"]["S"] == ["N11", "N14", "N09", "N15", "N13"]
    assert e["variante_c"]["a_prima"] == pytest.approx({"N11": 7.96, "N14": 10.48, "N09": 10.26, "N15": 9.7,
                                                         "N13": 8.54})
    assert e["reparto"]["x"] == {"N11": 5, "N14": 7, "N09": 7, "N15": 6, "N13": 5}
    assert e["reparto"]["utilidad"] == pytest.approx(91.566977, abs=1e-6)
    assert e["exacto"]["disponible"] and e["exacto"]["repartos"] == REPARTOS_PROFESORA
    assert e["exacto"]["OPT"] == pytest.approx(e["reparto"]["utilidad"], rel=1e-12)


def test_evidencia_c2_de_la_docente():
    e = _evidencia("c2")
    assert e["todas_cumplen"] and e["seleccion"]["S"] == ["N11", "N14", "N09", "N15", "N13"]
    assert e["reparto"]["x"] == {"N11": 4, "N14": 8, "N09": 7, "N15": 6, "N13": 5}
    assert e["reparto"]["utilidad"] == pytest.approx(99.247037, abs=1e-6)
    assert (e["reparto"]["pasos"], e["reparto"]["ganancias_recalculadas"], e["reparto"]["revisados"]) == (30, 155, 150)
    assert e["exacto"]["x"] == e["reparto"]["x"] and e["exacto"]["repartos"] == REPARTOS_PROFESORA
    assert e["reparto_base"]["utilidad_con_vecinos"] == pytest.approx(99.224645, abs=1e-6)


def test_la_corrida_de_la_docente_reproduce_la_evidencia_de_c2():
    """La misma corrida que dejó la evidencia (límite = 302792, el número exacto de repartos)."""
    r = ejecutar_variante_c(leer_instancia(PROFESORA), "c2", 0.2, 1, limite=REPARTOS_PROFESORA)
    e = _evidencia("c2")
    assert r["todas_cumplen"] and r["reparto"]["x"] == e["reparto"]["x"]
    assert r["exacto"]["OPT"] == pytest.approx(e["exacto"]["OPT"], rel=1e-12)
    texto = a_texto_vecinos(r)
    assert "302792 repartos evaluados" in texto and "CUMPLEN" in texto
