"""Variante (a): costos de participación. Los cuatro algoritmos de red/variante_costos.py, sus conteos,
sus cotas contra el OPT, la integración en la ronda y en ejecutar.py, y el script de la tabla."""

import csv
import json
import os
import sys
from math import comb, e
from pathlib import Path

import pytest

from ejecutar import main
from red.cobertura import OraculoCobertura
from red.entrada import ErrorDeFormato, instancia_desde_diccionario, leer_instancia
from red.exacto import DemasiadasCombinaciones, seleccionar_exacto
from red.generador import generar_instancia_influencia
from red.ronda import NO_SE_APLICA, SE_APLICA_A, ejecutar_ronda
from red.seleccion import seleccionar_nodos
from red.traza import Traza, a_texto
from red.variante_costos import (enumeracion_parcial, seleccionar_exacto_costos, voraz_modificado,
                                 voraz_por_cociente)

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import tabla_cota_variante_a  # noqa: E402

PROFESORA = RAIZ / "casos" / "profesora" / "entrada_G2_red_15_nodos.json"
PROPIOS = sorted(f for f in os.listdir(RAIZ / "casos" / "propios") if f.endswith(".json"))
# 2^N ≤ 200000 exige N ≤ 17: quedan fuera los sintéticos (N ≥ 20)
PEQUENOS = [RAIZ / "casos" / "propios" / f for f in PROPIOS
            if leer_instancia(RAIZ / "casos" / "propios" / f).N <= 17]
CASOS = PEQUENOS + [PROFESORA]
COTA_E = 1 - 1 / e


def _costos_unitarios(inst):
    return {v: 1 for v in inst.ids()}


# ---------- Con todos los costos en 1 y L = k, la variante se reduce a la solución base ----------

@pytest.mark.parametrize("ruta", CASOS, ids=lambda r: Path(r).stem)
def test_con_costos_1_y_L_k_la_fuerza_bruta_da_el_mismo_OPT_que_exacto(ruta):
    inst = leer_instancia(ruta)
    ids, k = inst.ids(), inst.k
    _, opt_k, _ = seleccionar_exacto(inst.crear_oraculo(), ids, k)
    S, opt, evaluaciones = seleccionar_exacto_costos(inst.crear_oraculo(), ids, _costos_unitarios(inst), k)
    assert opt == pytest.approx(opt_k, rel=1e-9)
    assert len(S) <= k
    assert evaluaciones == sum(comb(inst.N, j) for j in range(k + 1))   # todos los factibles, incluido ∅


@pytest.mark.parametrize("ruta", CASOS, ids=lambda r: Path(r).stem)
def test_con_costos_1_y_L_k_el_cociente_y_el_modificado_son_el_voraz_base(ruta):
    inst = leer_instancia(ruta)
    ids, k = inst.ids(), inst.k
    S_base, f_base = seleccionar_nodos(inst.crear_oraculo(), ids, k)
    cociente = voraz_por_cociente(inst.crear_oraculo(), ids, _costos_unitarios(inst), k)
    modificado = voraz_modificado(inst.crear_oraculo(), ids, _costos_unitarios(inst), k)
    assert cociente.S == S_base and cociente.valor == pytest.approx(f_base, rel=1e-9)
    assert modificado.S == S_base and modificado.origen == "cociente"
    # el conteo del voraz base, k·N − k(k−1)/2, más la evaluación de f(∅)
    assert cociente.evaluaciones == modificado.evaluaciones == 1 + k * inst.N - k * (k - 1) // 2


@pytest.mark.parametrize("ruta", CASOS, ids=lambda r: Path(r).stem)
def test_con_costos_1_y_L_k_la_enumeracion_queda_entre_el_voraz_y_el_OPT(ruta):
    inst = leer_instancia(ruta)
    ids, k = inst.ids(), inst.k
    _, f_base = seleccionar_nodos(inst.crear_oraculo(), ids, k)
    _, opt, _ = seleccionar_exacto(inst.crear_oraculo(), ids, k)
    enumeracion = enumeracion_parcial(inst.crear_oraculo(), ids, _costos_unitarios(inst), k)
    assert f_base - 1e-9 <= enumeracion.valor <= opt + 1e-9
    assert sum(1 for _ in enumeracion.S) <= k


# ---------- Conteos exactos del peor caso (todo cabe) ----------

@pytest.mark.parametrize("N", [4, 6, 9])
def test_conteos_del_peor_caso_cuando_todo_cabe(N):
    V = list(range(1, N + 1))
    costos = {v: 1 for v in V}
    conjuntos = {v: {f"e{v}", f"e{v + 1}"} for v in V}
    _, _, ev_exacto = seleccionar_exacto_costos(OraculoCobertura(conjuntos), V, costos, N)
    assert ev_exacto == 2 ** N
    cociente = voraz_por_cociente(OraculoCobertura(conjuntos), V, costos, N)
    assert cociente.S and len(cociente.S) == N
    assert cociente.evaluaciones == 1 + N * (N + 1) // 2
    enumeracion = enumeracion_parcial(OraculoCobertura(conjuntos), V, costos, N)
    assert enumeracion.evaluaciones == 1 + N + comb(N, 2) + comb(N, 3) * (1 + (N - 3) * (N - 2) // 2)


def test_los_contadores_coinciden_con_los_del_oraculo():
    V = [1, 2, 3, 4, 5]
    costos = {1: 2, 2: 3, 3: 1, 4: 4, 5: 2}
    conjuntos = {1: {"a", "b"}, 2: {"b", "c", "d"}, 3: {"d"}, 4: {"a", "e", "f", "g"}, 5: {"g", "h"}}
    for algoritmo in (voraz_por_cociente, voraz_modificado, enumeracion_parcial):
        oraculo = OraculoCobertura(conjuntos)
        r = algoritmo(oraculo, V, costos, 5)
        assert r.evaluaciones == oraculo.llamadas_ganancia + oraculo.llamadas_valor
        assert r.costo == sum(costos[v] for v in r.S) <= 5
    oraculo = OraculoCobertura(conjuntos)
    _, _, evaluaciones = seleccionar_exacto_costos(oraculo, V, costos, 5)
    assert evaluaciones == oraculo.llamadas_valor


def test_mejor_caso_nada_cabe():
    V = [1, 2, 3]
    oraculo = OraculoCobertura({1: {"a"}, 2: {"b"}, 3: {"c"}})
    costos = {1: 5, 2: 5, 3: 5}
    assert seleccionar_exacto_costos(oraculo, V, costos, 4) == ([], 0, 1)
    r = voraz_por_cociente(oraculo, V, costos, 4)
    assert r.S == [] and r.valor == 0 and r.costo == 0 and r.evaluaciones == 1 and r.mejor_solo is None
    assert voraz_modificado(oraculo, V, costos, 4).S == []
    r = enumeracion_parcial(oraculo, V, costos, 4)
    assert r.S == [] and r.evaluaciones == 1


# ---------- Fuerza bruta: poda, límite y empates ----------

def test_fuerza_bruta_evalua_solo_los_factibles():
    V = [1, 2, 3, 4]
    costos = {1: 1, 2: 2, 3: 3, 4: 4}
    oraculo = OraculoCobertura({v: {v} for v in V})
    S, opt, evaluaciones = seleccionar_exacto_costos(oraculo, V, costos, 4)
    # factibles con Σ c ≤ 4: ∅, {1}, {2}, {3}, {4}, {1,2}, {1,3}
    assert evaluaciones == 7
    assert opt == 2 and S == [1, 2]   # {1,2} va antes que {1,3} en orden lexicográfico


def test_fuerza_bruta_empate_gana_el_primero_lexicografico():
    oraculo = OraculoCobertura({1: {"a"}, 2: {"a"}, 3: {"b"}})
    S, opt, _ = seleccionar_exacto_costos(oraculo, [1, 2, 3], {1: 1, 2: 1, 3: 1}, 1)
    assert S == [1] and opt == 1


def test_fuerza_bruta_se_niega_si_2_elevado_N_supera_el_limite():
    V = list(range(1, 19))   # 2^18 = 262144 > 200000
    oraculo = OraculoCobertura({v: {v} for v in V})
    with pytest.raises(DemasiadasCombinaciones, match="supera el límite"):
        seleccionar_exacto_costos(oraculo, V, {v: 1 for v in V}, 3)
    assert oraculo.llamadas_valor == 0


# ---------- El cociente no tiene garantía; el modificado lo corrige ----------

@pytest.mark.parametrize("M", [10, 100, 1000])
def test_contraejemplo_del_cociente_tan_malo_como_se_quiera(M):
    # Nodo 1: barato (c = 1) y cubre 2 elementos: cociente 2. Nodo 2: ocupa todo L = M y cubre 2M − 1:
    # cociente (2M − 1)/M < 2. El cociente toma al 1, luego el 2 ya no cabe: f = 2 contra OPT = 2M − 1.
    conjuntos = {1: {"a", "b"}, 2: {f"x{j}" for j in range(2 * M - 1)}}
    costos = {1: 1, 2: M}
    cociente = voraz_por_cociente(OraculoCobertura(conjuntos), [1, 2], costos, M)
    assert cociente.S == [1] and cociente.valor == 2
    _, opt, _ = seleccionar_exacto_costos(OraculoCobertura(conjuntos), [1, 2], costos, M)
    assert opt == 2 * M - 1
    assert cociente.valor / opt < 2.1 / M          # tiende a 0 cuando M crece
    modificado = voraz_modificado(OraculoCobertura(conjuntos), [1, 2], costos, M)
    assert modificado.S == [2] and modificado.valor == opt and modificado.origen == "mejor_nodo_solo"
    assert modificado.evaluaciones == cociente.evaluaciones   # el mejor nodo solo no cuesta evaluaciones


def test_desempate_del_cociente_por_el_menor_indice():
    oraculo = OraculoCobertura({1: {"a"}, 2: {"b"}, 3: {"c", "d"}})
    r = voraz_por_cociente(oraculo, [1, 2, 3], {1: 1, 2: 1, 3: 2}, 1)   # todos con cociente 1; el 3 no cabe
    assert r.S == [1]


def test_los_que_no_caben_se_saltan_y_se_sigue():
    oraculo = OraculoCobertura({1: {"a", "b", "c"}, 2: {"d", "e"}, 3: {"f"}})
    r = voraz_por_cociente(oraculo, [1, 2, 3], {1: 3, 2: 2, 3: 1}, 4)
    assert r.S == [1, 3] and r.costo == 4 and r.valor == 4   # tras el 1 (c = 3) ya no cabe el 2, pero sí el 3


# ---------- Cotas contra el OPT: profesora y batería aleatoria ----------

def test_profesora_con_L_24_razones_y_resultado():
    fila = tabla_cota_variante_a.fila_de_la_profesora()
    assert fila["N"] == 15 and fila["L"] == 24
    assert fila["OPT"] == pytest.approx(146.27141, abs=1e-5) and fila["costo_OPT"] == 23
    assert fila["razon_modificado"] >= 0.405 and fila["razon_enumeracion"] >= COTA_E
    assert fila["cumple"]
    inst = leer_instancia(PROFESORA)
    r = voraz_modificado(inst.crear_oraculo(), inst.ids(), inst.costos(), 24)
    assert r.S == ["N05", "N09", "N14", "N11", "N15", "N01"] and r.costo == 21 and r.evaluaciones == 74
    assert r.valor == pytest.approx(145.9911, abs=1e-4)


@pytest.fixture(scope="module")
def bateria():
    return tabla_cota_variante_a.bateria_aleatoria()


def test_bateria_aleatoria_cumple_las_cotas(bateria):
    assert len(bateria) == 36 and len({f["caso"] for f in bateria}) == 36
    for f in bateria:
        assert f["razon_cociente"] <= 1 + 1e-6 and f["razon_enumeracion"] <= 1 + 1e-6
        assert f["razon_modificado"] >= 0.405 - 1e-9, f["caso"]
        assert f["razon_enumeracion"] >= COTA_E - 1e-9, f["caso"]
        assert f["f_modificado"] >= f["f_cociente"] - 1e-9
        assert f["cumple"]


def test_bateria_es_reproducible_y_el_csv_tiene_las_columnas(bateria, tmp_path):
    assert tabla_cota_variante_a.bateria_aleatoria(tamanos=(10,), densidades=(0.6,), semillas=(1,)) == \
        [f for f in bateria if f["N"] == 10 and f["densidad"] == 0.6 and f["semilla"] == 1]
    ruta = tmp_path / "t.csv"
    tabla_cota_variante_a.escribir_csv(ruta, tabla_cota_variante_a.COLUMNAS, bateria)
    with open(ruta, newline="", encoding="utf-8") as a:
        lector = csv.DictReader(a)
        assert lector.fieldnames == tabla_cota_variante_a.COLUMNAS
        assert len(list(lector)) == 36


def test_el_csv_del_repositorio_coincide_con_lo_que_genera_el_script(bateria):
    with open(RAIZ / "resultados" / "variantes" / "a_tabla_cota.csv", newline="", encoding="utf-8") as a:
        filas = list(csv.DictReader(a))
    assert len(filas) == 37 and filas[0]["caso"] == "entrada_G2_red_15_nodos"
    assert [f["caso"] for f in filas[1:]] == [f["caso"] for f in bateria]
    assert all(f["cumple"] == "True" for f in filas)


# ---------- Generador: presupuesto_costos opcional ----------

def test_generador_presupuesto_costos_opcional_no_cambia_lo_demas():
    base = generar_instancia_influencia(10, 3, 50, 0.5, 7)
    con_L = generar_instancia_influencia(10, 3, 50, 0.5, 7, presupuesto_costos=12)
    assert base["parametros"]["presupuesto_costos_participacion_por_ronda"] == 15
    assert con_L["parametros"]["presupuesto_costos_participacion_por_ronda"] == 12
    assert base["nodos"] == con_L["nodos"] and base["grafo"] == con_L["grafo"]
    with pytest.raises(ValueError):
        generar_instancia_influencia(10, 3, 50, 0.5, 7, presupuesto_costos=-1)


# ---------- Entrada: campos opcionales del formato propio ----------

def _propio(costos=(1, 2, 3), L=4, **extra):
    nodos = [{"id": i + 1, "cubre": [f"e{i}", f"e{i + 1}"], "utilidad": {"tipo": "log", "a": 2.0}}
             for i in range(3)]
    for nodo, c in zip(nodos, costos):
        if c is not None:
            nodo["costo"] = c
    datos = {"k": 2, "B": 4, "nodos": nodos}
    if L is not None:
        datos["presupuesto_costos"] = L
    datos.update(extra)
    return datos


def test_formato_propio_sin_los_campos_queda_como_hoy():
    inst = instancia_desde_diccionario(_propio(costos=(None, None, None), L=None))
    assert inst.costos() == {} and inst.presupuesto_costos is None
    r = ejecutar_ronda(inst, repeticiones=1)
    assert r["todas_cumplen"] and "variante" not in r and "L" not in r["entrada"]


def test_formato_propio_lee_costo_y_presupuesto_costos():
    inst = instancia_desde_diccionario(_propio())
    assert inst.costos() == {1: 1, 2: 2, 3: 3} and inst.presupuesto_costos == 4
    with pytest.raises(ErrorDeFormato, match="costo"):
        instancia_desde_diccionario(_propio(costos=("3", 2, 3)))
    with pytest.raises(ErrorDeFormato, match="presupuesto_costos"):
        instancia_desde_diccionario(_propio(L=float("nan")))


def test_formato_de_la_profesora_lee_L():
    inst = leer_instancia(PROFESORA)
    assert inst.presupuesto_costos == 24 and inst.costos()["N01"] == 3 and len(inst.costos()) == 15


# ---------- Ronda y ejecutar.py con --variante a ----------

def test_ronda_base_no_cambia_con_la_variante_None():
    r = ejecutar_ronda(leer_instancia(PROFESORA), repeticiones=1)
    assert "variante" not in r and "costo" not in r["seleccion"]
    assert r["informativo"]["variante_a"]["nota"] == NO_SE_APLICA
    with pytest.raises(ValueError, match="variante desconocida"):
        ejecutar_ronda(leer_instancia(PROFESORA), repeticiones=1, variante="z")


def test_ronda_variante_a_sobre_la_profesora():
    r = ejecutar_ronda(leer_instancia(PROFESORA), repeticiones=2, variante="a")
    assert r["todas_cumplen"]
    assert r["entrada"]["L"] == 24 and r["variante"]["nombre"] == "a" and r["variante"]["L"] == 24
    s = r["seleccion"]
    assert s["S"] == ["N05", "N09", "N14", "N11", "N15", "N01"] and s["costo"] == 21 and s["origen"] == "cociente"
    assert s["evaluaciones"] == 74 and r["reparto"]["x"] == {"N05": 4, "N09": 6, "N14": 6, "N11": 4, "N15": 5, "N01": 5}
    nombres = [v["nombre"] for v in r["verificaciones"]["seleccion"]]
    assert any("Σ c(S) ≤ L" in n for n in nombres) and not any("|S| ≤ k" == n for n in nombres)
    assert r["informativo"]["variante_a"]["nota"] == SE_APLICA_A
    texto = a_texto(r)
    assert "VARIANTE (a)" in texto and "Δ/c(N05) = 82.6000/2 = 41.3000" in texto and "Σ c(S) = 21 ≤ L = 24" in texto
    assert r["traza"]["pasos_seleccion"][0]["costo_despues"] == 2


def test_ronda_variante_a_rechaza_costo_no_positivo_y_L_ausente():
    r = ejecutar_ronda(instancia_desde_diccionario(_propio(costos=(1, 0, 3))), repeticiones=1, variante="a")
    assert "seleccion" not in r and not r["todas_cumplen"]
    assert any("costo" in m and "2" in m for m in r["traza"]["motivo_rechazo"])
    r = ejecutar_ronda(instancia_desde_diccionario(_propio(L=None)), repeticiones=1, variante="a")
    assert "seleccion" not in r and any("presupuesto_costos" in m for m in r["traza"]["motivo_rechazo"])
    # sin la variante, esos mismos archivos corren como siempre
    assert ejecutar_ronda(instancia_desde_diccionario(_propio(costos=(1, 0, 3))), repeticiones=1)["todas_cumplen"]


def test_ronda_variante_a_en_el_formato_propio():
    r = ejecutar_ronda(instancia_desde_diccionario(_propio(costos=(3, 2, 1), L=3)), repeticiones=1, variante="a")
    assert r["todas_cumplen"]
    assert r["seleccion"]["costo"] <= 3 and len(r["seleccion"]["S"]) >= 1


def test_ejecutar_con_variante_a_escribe_las_evidencias(tmp_path):
    salida = tmp_path / "a"
    assert main([str(PROFESORA), "--salida", str(salida), "--repeticiones", "2", "--variante", "a"]) == 0
    with open(salida / "entrada_G2_red_15_nodos" / "salida.json", encoding="utf-8") as a:
        datos = json.load(a)
    assert datos["variante"]["L"] == 24 and datos["seleccion"]["costo"] == 21
    assert "VARIANTE (a)" in (salida / "entrada_G2_red_15_nodos" / "traza.txt").read_text(encoding="utf-8")
    with open(salida / "resumen.csv", newline="", encoding="utf-8") as a:
        filas = list(csv.DictReader(a))
    assert filas[0]["S"] == "N05 N09 N14 N11 N15 N01" and filas[0]["todas_cumplen"] == "True"


def test_traza_paso_seleccion_costos_guarda_el_cociente():
    traza = Traza()
    traza.paso_seleccion_costos(1, [(1, 4.0, 2), (2, 3.0, 1)], 2, 3.0, 3.0, 1)
    paso = traza.a_diccionario()["pasos_seleccion"][0]
    assert paso["aportes"][0] == {"nodo": 1, "ganancia": 4.0, "costo": 2, "cociente": 2.0}
    assert paso["elegido"] == 2 and paso["costo_despues"] == 1
