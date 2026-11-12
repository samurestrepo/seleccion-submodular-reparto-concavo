"""Pruebas de scripts/tabla_cota.py: la batería aleatoria de la cota (decisión 34)."""

import csv
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import tabla_cota  # noqa: E402


@pytest.fixture(scope="module")
def filas():
    return tabla_cota.bateria_aleatoria()


def test_la_bateria_tiene_45_filas_con_casos_distintos(filas):
    assert len(filas) == 45
    assert len({f["caso"] for f in filas}) == 45


def test_es_reproducible(filas):
    assert tabla_cota.bateria_aleatoria() == filas


def test_voraz_nunca_supera_al_optimo(filas):
    assert all(f["f_voraz"] <= f["OPT"] + 1e-6 for f in filas)


def test_razon_en_cero_uno(filas):
    assert all(0 < f["razon"] <= 1 for f in filas)


def test_todas_cumplen_la_cota(filas):
    assert all(f["cumple"] for f in filas)


def test_el_csv_nuevo_tiene_las_columnas_pedidas(filas, tmp_path):
    ruta = tmp_path / "t.csv"
    tabla_cota.escribir_csv(ruta, tabla_cota.COLUMNAS_ALEATORIA, filas)
    with open(ruta, newline="", encoding="utf-8") as a:
        lector = csv.DictReader(a)
        assert lector.fieldnames == ["caso", "N", "k", "densidad", "semilla", "f_voraz", "OPT",
                                     "razon", "cota_k", "cota_e", "cumple"]
        assert len(list(lector)) == 45
