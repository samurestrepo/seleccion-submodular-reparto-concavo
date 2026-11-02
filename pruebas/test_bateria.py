"""La batería de casos de casos/: los válidos salen en OK y los inválidos se rechazan."""

import os
from pathlib import Path

import pytest

from ejecutar import main
from red.entrada import leer_instancia
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
