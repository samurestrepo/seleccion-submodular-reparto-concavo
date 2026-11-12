"""El algoritmo exacto por fuerza bruta y la cota del voraz contra el óptimo real."""

import os
from math import comb, e
from pathlib import Path

import pytest

from red.entrada import leer_instancia
from red.exacto import DemasiadasCombinaciones, seleccionar_exacto
from red.seleccion import seleccionar_nodos

RAIZ = Path(__file__).resolve().parent.parent
PROFESORA = RAIZ / "casos" / "profesora" / "entrada_G2_red_15_nodos.json"
PROPIOS = sorted(f for f in os.listdir(RAIZ / "casos" / "propios") if f.endswith(".json"))
PEQUENOS = [
    RAIZ / "casos" / "propios" / f
    for f in PROPIOS
    if leer_instancia(RAIZ / "casos" / "propios" / f).N <= 20
]
CASOS_COTA = PEQUENOS + [PROFESORA]


def _exacto_y_voraz(ruta):
    inst = leer_instancia(ruta)
    ids = inst.ids()
    S_voraz, f_voraz = seleccionar_nodos(inst.crear_oraculo(), ids, inst.k)
    S_opt, opt, evaluaciones = seleccionar_exacto(inst.crear_oraculo(), ids, inst.k)
    return inst, f_voraz, opt, S_opt, evaluaciones


@pytest.mark.parametrize("N, k", [(5, 2), (6, 3), (7, 1), (7, 7), (8, 4)])
def test_conteo_de_evaluaciones_es_c_n_k(N, k):
    from red.cobertura import OraculoCobertura
    conjuntos = {v: {v, v + 1} for v in range(1, N + 1)}
    oraculo = OraculoCobertura(conjuntos)
    _, _, evaluaciones = seleccionar_exacto(oraculo, list(range(1, N + 1)), k)
    assert evaluaciones == comb(N, k)
    assert oraculo.llamadas_valor == comb(N, k)


@pytest.mark.parametrize("ruta", CASOS_COTA, ids=lambda r: Path(r).stem)
def test_voraz_cumple_la_cota_contra_el_optimo(ruta):
    inst, f_voraz, opt, _, evaluaciones = _exacto_y_voraz(ruta)
    assert evaluaciones == comb(inst.N, inst.k)
    assert f_voraz <= opt + 1e-9
    cota_k = 1 - (1 - 1 / inst.k) ** inst.k
    assert cota_k >= 1 - 1 / e - 1e-12
    if opt > 0:
        assert f_voraz / opt >= cota_k - 1e-9


def test_contraejemplo_seleccion_da_opt_6():
    inst = leer_instancia(RAIZ / "casos" / "propios" / "contraejemplo_seleccion.json")
    S_opt, opt, _ = seleccionar_exacto(inst.crear_oraculo(), inst.ids(), inst.k)
    assert opt == 6
    assert S_opt == [2, 3]


def test_empate_gana_el_primero_lexicografico():
    from red.cobertura import OraculoCobertura
    oraculo = OraculoCobertura({1: {"a"}, 2: {"b"}, 3: {"c"}})
    S_opt, opt, _ = seleccionar_exacto(oraculo, [1, 2, 3], 2)
    assert S_opt == [1, 2] and opt == 2


def test_se_niega_si_hay_demasiadas_combinaciones():
    from red.cobertura import OraculoCobertura
    V = list(range(1, 41))
    oraculo = OraculoCobertura({v: {v} for v in V})
    with pytest.raises(DemasiadasCombinaciones, match="supera el límite"):
        seleccionar_exacto(oraculo, V, 20)
    assert oraculo.llamadas_valor == 0
