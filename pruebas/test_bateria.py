"""La batería de casos de casos/: los válidos salen en OK y los inválidos se rechazan."""

import json
import math
import os
from pathlib import Path

import pytest

from ejecutar import main
from red.entrada import leer_instancia
from red.reparto import repartir_presupuesto
from red.ronda import ejecutar_ronda
from red.traza import a_texto

RAIZ = Path(__file__).resolve().parent.parent
PROPIOS = sorted(f for f in os.listdir(RAIZ / "casos" / "propios") if f.endswith(".json"))
INVALIDOS = sorted(f for f in os.listdir(RAIZ / "casos" / "invalidos") if f.endswith(".json"))

# Resultados esperados de los casos pensados a mano: (S, f(S), reparto)
ESPERADOS = {
    "ejemplo_informe.json": ([1, 3], 5, {"1": 3, "3": 1}),
    "reparto_P_Q_informe.json": ([1, 2], 5, {"1": 2, "2": 2}),
    "contraejemplo_seleccion.json": ([1, 2], 5, {"1": 2, "2": 2}),
    "borde_B_cero.json": ([1, 2], 3, {"1": 0, "2": 0}),
    "borde_k_uno.json": ([2], 3, {"2": 5}),
    "borde_nodo_sin_cobertura.json": ([2, 3], 3, None),
    "empates.json": ([1, 2], 2, {"1": 2, "2": 2}),
    "tope_activo.json": ([1, 2], 3, {"1": 2, "2": 3}),
}


@pytest.mark.parametrize("archivo", PROPIOS)
def test_casos_propios_cumplen(archivo):
    r = ejecutar_ronda(leer_instancia(RAIZ / "casos" / "propios" / archivo))
    assert r["todas_cumplen"]
    if archivo in ESPERADOS:
        S, valor, x = ESPERADOS[archivo]
        assert r["seleccion"]["S"] == S
        assert r["seleccion"]["valor"] == valor
        if x is not None:
            assert r["reparto"]["x"] == x


def test_utilidad_del_reparto_P_Q_es_27():
    r = ejecutar_ronda(leer_instancia(RAIZ / "casos" / "propios" / "reparto_P_Q_informe.json"))
    assert r["reparto"]["utilidad"] == 27


@pytest.mark.parametrize("archivo", INVALIDOS)
def test_casos_invalidos_se_rechazan(archivo):
    r = ejecutar_ronda(leer_instancia(RAIZ / "casos" / "invalidos" / archivo))
    assert not r["todas_cumplen"]
    assert "seleccion" not in r
    assert "Caso rechazado" in a_texto(r)


def test_invalidos_dejan_traza_txt(tmp_path):
    assert main([str(RAIZ / "casos" / "invalidos"), "--salida", str(tmp_path)]) == 1
    for archivo in INVALIDOS:
        assert (tmp_path / archivo.removesuffix(".json") / "traza.txt").exists()


# Regresión del caso oficial: valores calculados aparte, antes de escribir el código
CASO_PROFESORA = RAIZ / "casos" / "profesora" / "entrada_G2_red_15_nodos.json"


def test_regresion_caso_de_la_profesora():
    r = ejecutar_ronda(leer_instancia(CASO_PROFESORA))
    assert r["todas_cumplen"]
    assert r["entrada"] == {"N": 15, "k": 5, "B": 30}
    assert r["seleccion"]["S"] == ["N11", "N14", "N09", "N15", "N13"]
    assert r["seleccion"]["valor"] == pytest.approx(145.5795, abs=5e-5)
    assert r["seleccion"]["llamadas_ganancia"] == 65
    assert r["reparto"]["x"] == {"N11": 5, "N14": 7, "N09": 7, "N15": 6, "N13": 5}
    assert r["reparto"]["utilidad"] == pytest.approx(88.5640, abs=5e-5)
    assert r["reparto"]["extracciones"] == 30
    assert r["reparto"]["inserciones"] == 30
    assert r["informativo"]["variante_a"]["suma_costos_de_S"] == 23
    assert r["informativo"]["variante_a"]["presupuesto_costos_participacion_por_ronda"] == 24
    assert r["informativo"]["variante_b"]["numero_rondas"] == 3


def test_el_caso_de_la_profesora_corre_por_la_linea_de_comandos(tmp_path):
    assert main([str(CASO_PROFESORA), "--salida", str(tmp_path)]) == 0
    carpeta = tmp_path / CASO_PROFESORA.stem
    salida = json.loads((carpeta / "salida.json").read_text(encoding="utf-8"))
    assert salida["informativo"]["variante_a"]["suma_costos_de_S"] == 23
    assert "== Informativo" in (carpeta / "traza.txt").read_text(encoding="utf-8")
    assert "N11 N14 N09 N15 N13" in (tmp_path / "resumen.csv").read_text(encoding="utf-8")


def test_el_tope_no_cambia_el_caso_de_la_profesora():
    # Se comprueba con el archivo real: cada presupuesto_total_nodo es 18, y nadie llega ahí
    instancia = leer_instancia(CASO_PROFESORA)
    topes = instancia.topes()
    assert len(topes) == 15
    assert set(topes.values()) == {18}
    r = ejecutar_ronda(instancia)
    assert max(r["reparto"]["x"].values()) < 18
    S = r["seleccion"]["S"]
    sin_topes = repartir_presupuesto(S, instancia.B, instancia.utilidades())
    assert r["reparto"]["x"] == sin_topes.x
    assert r["reparto"]["utilidad"] == sin_topes.utilidad
    assert (r["reparto"]["extracciones"], r["reparto"]["inserciones"]) == (30, 30)


def test_el_tope_si_cambia_el_caso_tope_activo():
    # Dos nodos log con a = 10 (tope 2) y a = 1, B = 5. El nodo 3 existe porque se exige k < N
    instancia = leer_instancia(RAIZ / "casos" / "propios" / "tope_activo.json")
    assert instancia.topes() == {1: 2}
    r = ejecutar_ronda(instancia)
    assert r["todas_cumplen"]
    assert r["reparto"]["x"] == {"1": 2, "2": 3}
    assert r["reparto"]["extracciones"] == 5
    assert r["reparto"]["inserciones"] == 4
    assert r["reparto"]["utilidad"] == pytest.approx(10 * math.log(3) + math.log(4))
    sin_topes = repartir_presupuesto(r["seleccion"]["S"], instancia.B, instancia.utilidades())
    assert sin_topes.x == {1: 5, 2: 0}   # sin el tope, todo iría al nodo 1
