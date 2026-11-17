"""Pruebas de scripts/corrida_combinada.py: las variantes (a) + (b) + (c) juntas (decisiones 56 y 57)."""

import copy
import json
import math
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import corrida_combinada  # noqa: E402
from red.entrada import instancia_desde_diccionario, leer_instancia  # noqa: E402
from red.reparto import repartir_presupuesto  # noqa: E402
from red.seleccion import seleccionar_nodos  # noqa: E402

CASO = RAIZ / "casos" / "profesora" / "entrada_G2_red_15_nodos.json"


@pytest.fixture(scope="module")
def datos():
    with open(CASO, encoding="utf-8") as archivo:
        return json.load(archivo)


@pytest.fixture(scope="module")
def instancia():
    return leer_instancia(CASO)


def _con_costos_unitarios(datos):
    """El caso de la docente con c(v) = 1 y L = k: la restricción de costos es |S| ≤ k."""
    d = copy.deepcopy(datos)
    for nodo in d["nodos"]:
        nodo["costo_participacion"] = 1
    d["parametros"]["presupuesto_costos_participacion_por_ronda"] = d["parametros"]["cupo_participantes_por_ronda_k"]
    return instancia_desde_diccionario(d, "unitario")


@pytest.mark.parametrize("modelo", ["c1", "c2"])
def test_con_q_0_T_1_beta_0_y_costos_1_reproduce_la_base(datos, modelo):
    inst = _con_costos_unitarios(datos)
    r = corrida_combinada.ejecutar_combinada(inst, modelo, prob_fallo=0, rondas=1, beta=0)
    S, valor = seleccionar_nodos(inst.crear_oraculo(), inst.ids(), inst.k)
    base = repartir_presupuesto(S, inst.B, inst.utilidades(), topes=inst.topes())
    ronda = r["rondas"][0]
    assert ronda["fallados"] == [] and ronda["seleccion"]["S"] == S
    assert math.isclose(ronda["seleccion"]["valor"], valor)
    assert ronda["reparto"]["x"] == base.x
    assert math.isclose(ronda["reparto"]["U"], base.utilidad)
    assert r["todas_cumplen"]


@pytest.mark.parametrize("modelo", ["c1", "c2"])
def test_costo_de_cada_S_r_cabe_en_L_y_S_r_sale_de_los_candidatos(instancia, modelo):
    r = corrida_combinada.ejecutar_combinada(instancia, modelo)
    costos, L = instancia.costos(), instancia.presupuesto_costos
    for ronda in r["rondas"]:
        S = ronda["seleccion"]["S"]
        assert sum(costos[v] for v in S) <= L
        assert set(S) <= set(ronda["candidatos"])
        assert not set(ronda["candidatos"]) & set(ronda["fallados"])
    assert r["todas_cumplen"]


@pytest.mark.parametrize("modelo", ["c1", "c2"])
def test_el_restante_nunca_es_negativo_aunque_se_agote(instancia, modelo):
    # 15 nodos con tope 18 suman 270 = 9 rondas de B = 30: con T = 12 el presupuesto se agota
    r = corrida_combinada.ejecutar_combinada(instancia, modelo, rondas=12, exacto=False)
    anterior = {v: 18 for v in instancia.ids()}
    for ronda in r["rondas"]:
        assert all(valor >= 0 for valor in ronda["restante"].values())
        assert all(anterior[v] > 0 for v in ronda["candidatos"])          # sin restante no es candidato
        assert all(x <= anterior[v] for v, x in ronda["reparto"]["x"].items())   # tope = restante
        anterior = {v: int(valor) for v, valor in ronda["restante"].items()}
    assert r["rondas"][-1]["restante_total"] == 0                           # se agotó
    assert r["todas_cumplen"]


def test_es_reproducible_con_la_misma_semilla(instancia):
    a = corrida_combinada.ejecutar_combinada(instancia, "c2", semilla=7, exacto=False)
    b = corrida_combinada.ejecutar_combinada(instancia, "c2", semilla=7, exacto=False)
    assert a == b


def test_con_q_1_nadie_participa(instancia):
    r = corrida_combinada.ejecutar_combinada(instancia, "c1", prob_fallo=1)
    for ronda in r["rondas"]:
        assert ronda["candidatos"] == [] and ronda["seleccion"]["S"] == [] and ronda["reparto"]["U"] == 0.0
    assert r["rondas"][-1]["restante_total"] == 270


def test_el_formato_propio_se_rechaza():
    propio = {"k": 1, "B": 2, "nodos": [{"id": 1, "cubre": ["a"], "utilidad": {"tipo": "log", "a": 1}, "costo": 1}],
              "presupuesto_costos": 1}
    with pytest.raises(ValueError):
        corrida_combinada.ejecutar_combinada(instancia_desde_diccionario(propio), "c1")
