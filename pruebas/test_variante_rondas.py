"""Variante (b): T rondas con nodos que fallan (red/variante_rondas.py). Reducción a la solución base con
q = 0 y T = 1, sorteo de fallos, presupuesto restante, modos transitorio y permanente, cota por ronda contra
OPT_r en una batería aleatoria, entrada (numero_rondas / rondas), ejecutar.py --variante b y las evidencias."""

import csv
import json
import os
import random
from pathlib import Path

import pytest

from ejecutar import main
from red.entrada import ErrorDeFormato, instancia_desde_diccionario, leer_instancia
from red.generador import generar_instancia_influencia
from red.ronda import ejecutar_ronda
from red.variante_rondas import (MODOS, a_texto_rondas, candidatos_de_la_ronda, ejecutar_rondas,
                                 sortear_fallos)
from red.verificacion import verificar_cota_ronda, verificar_seleccion_ronda, verificar_variante_b

RAIZ = Path(__file__).resolve().parent.parent
PROFESORA = RAIZ / "casos" / "profesora" / "entrada_G2_red_15_nodos.json"
PROPIOS = sorted(RAIZ / "casos" / "propios" / f for f in os.listdir(RAIZ / "casos" / "propios")
                 if f.endswith(".json"))
# borde_B_cero queda aparte: con B = 0 y sin topes, el restante arranca en 0 y no hay candidatos (ver abajo)
CASOS = [r for r in PROPIOS if r.stem != "borde_B_cero"] + [PROFESORA]
EVIDENCIAS = RAIZ / "resultados" / "variantes"


def _propio(k=2, B=4, topes=(None, None, None), **extra):
    """Tres nodos de cobertura con utilidad log; topes y campos extra opcionales."""
    nodos = [{"id": i + 1, "cubre": [f"e{i}", f"e{i + 1}"], "utilidad": {"tipo": "log", "a": 2.0}}
             for i in range(3)]
    for nodo, tope in zip(nodos, topes):
        if tope is not None:
            nodo["tope"] = tope
    datos = {"k": k, "B": B, "nodos": nodos}
    datos.update(extra)
    return datos


# ---------- q = 0 y T = 1 reproducen la solución base ----------

@pytest.mark.parametrize("ruta", CASOS, ids=lambda r: Path(r).stem)
def test_con_q_0_y_T_1_es_la_solucion_base(ruta):
    inst = leer_instancia(ruta)
    base = ejecutar_ronda(inst, repeticiones=1)
    r = ejecutar_rondas(inst, prob_fallo=0, rondas=1, repeticiones=1, exacto=False)
    assert r["todas_cumplen"] and len(r["rondas"]) == 1
    ronda = r["rondas"][0]
    assert ronda["fallados"] == [] and ronda["candidatos"] == inst.ids() and ronda["k_ronda"] == inst.k
    assert ronda["seleccion"]["S"] == base["seleccion"]["S"]
    assert ronda["seleccion"]["valor"] == base["seleccion"]["valor"]
    assert ronda["seleccion"]["llamadas_ganancia"] == base["seleccion"]["llamadas_ganancia"]
    assert ronda["reparto"]["x"] == base["reparto"]["x"]
    assert ronda["reparto"]["utilidad"] == base["reparto"]["utilidad"]


def test_con_B_0_y_sin_topes_no_hay_candidatos_a_diferencia_de_la_base():
    """Supuesto ❓ «sin tope, B»: con B = 0 todos arrancan con restante 0 y nadie puede participar.
    La base, en cambio, elige S (f(S) > 0) y reparte 0. Es la única diferencia con q = 0 y T = 1."""
    inst = leer_instancia(RAIZ / "casos" / "propios" / "borde_B_cero.json")
    base = ejecutar_ronda(inst, repeticiones=1)
    r = ejecutar_rondas(inst, prob_fallo=0, rondas=1, repeticiones=1)
    assert base["seleccion"]["S"] and base["reparto"]["utilidad"] == 0.0
    assert r["todas_cumplen"] and r["rondas"][0]["candidatos"] == [] and r["rondas"][0]["seleccion"]["S"] == []


def test_los_dos_modos_coinciden_con_q_0():
    inst = leer_instancia(PROFESORA)
    t = ejecutar_rondas(inst, modo="transitorio", prob_fallo=0, repeticiones=1, exacto=False)
    p = ejecutar_rondas(inst, modo="permanente", prob_fallo=0, repeticiones=1, exacto=False)
    assert [r["seleccion"]["S"] for r in t["rondas"]] == [r["seleccion"]["S"] for r in p["rondas"]]
    assert [r["presupuesto_restante"] for r in t["rondas"]] == [r["presupuesto_restante"] for r in p["rondas"]]


# ---------- Sorteo de fallos ----------

def test_sortear_fallos_q_0_nadie_y_q_1_todos_en_orden():
    ids = ["N03", "N01", "N02"]
    assert sortear_fallos(sorted(ids), 0, random.Random(5)) == []
    assert sortear_fallos(sorted(ids), 1, random.Random(5)) == ["N01", "N02", "N03"]


def test_sortear_fallos_es_reproducible_con_la_semilla():
    ids = list(range(50))
    a = sortear_fallos(ids, 0.3, random.Random(7))
    b = sortear_fallos(ids, 0.3, random.Random(7))
    c = sortear_fallos(ids, 0.3, random.Random(8))
    assert a == b and 0 < len(a) < 50 and a != c


def test_candidatos_excluyen_fuera_y_restante_0():
    assert candidatos_de_la_ronda([1, 2, 3, 4], {2}, {1: 5, 2: 5, 3: 0, 4: 1}) == [1, 4]


@pytest.mark.parametrize("modo", MODOS)
def test_q_1_deja_todas_las_rondas_sin_participantes(modo):
    inst = leer_instancia(PROFESORA)
    r = ejecutar_rondas(inst, modo=modo, prob_fallo=1, repeticiones=1)
    assert r["todas_cumplen"] and r["entrada"]["T"] == 3
    assert r["resumen"]["rondas_sin_participantes"] == 3
    for ronda in r["rondas"]:
        assert ronda["fallados"] == inst.ids() and ronda["candidatos"] == [] and ronda["k_ronda"] == 0
        assert ronda["seleccion"]["S"] == [] and ronda["seleccion"]["valor"] == 0.0
        assert ronda["seleccion"]["llamadas_ganancia"] == 0 and ronda["reparto"]["x"] == {}
        assert ronda["reparto"]["utilidad"] == 0.0 and ronda["exacto"]["OPT"] == 0.0 and ronda["razon"] is None
        assert all(x == 18 for x in ronda["presupuesto_restante"].values())
    assert r["resumen"]["suma_valores"] == 0.0 and "sin participantes" in a_texto_rondas(r)


# ---------- Presupuesto restante y modos ----------

def test_el_presupuesto_restante_se_descuenta_y_nunca_es_negativo():
    inst = leer_instancia(PROFESORA)
    r = ejecutar_rondas(inst, prob_fallo=0, rondas=8, repeticiones=1, exacto=False)
    assert r["todas_cumplen"]
    anterior = {v: 18 for v in inst.ids()}
    for ronda in r["rondas"]:
        restante = ronda["presupuesto_restante"]
        for v in inst.ids():
            gastado = ronda["reparto"]["x"].get(v, 0)
            assert restante[v] == anterior[v] - gastado and restante[v] >= 0
            assert gastado <= anterior[v]
        # los que ya no tienen presupuesto no son candidatos en la ronda siguiente
        anterior = restante
    agotados = [v for v, x in anterior.items() if x == 0]
    assert agotados, "con 8 rondas y topes de 18 alguien debe agotarse"
    gastado = sum(sum(ronda["reparto"]["x"].values()) for ronda in r["rondas"])
    assert sum(anterior.values()) == 15 * 18 - gastado and gastado <= 8 * 30


def test_un_nodo_sin_presupuesto_restante_no_es_candidato():
    inst = leer_instancia(PROFESORA)
    r = ejecutar_rondas(inst, prob_fallo=0, rondas=4, repeticiones=1, exacto=False)
    rondas = r["rondas"]
    for anterior, actual in zip(rondas, rondas[1:]):
        sin_presupuesto = {v for v, x in anterior["presupuesto_restante"].items() if x == 0}
        assert sin_presupuesto.isdisjoint(actual["candidatos"])
    assert any(x == 0 for x in rondas[2]["presupuesto_restante"].values())


def test_si_los_candidatos_son_k_o_menos_participan_todos():
    inst = instancia_desde_diccionario(_propio(k=2, topes=(None, 0, 0)))
    r = ejecutar_rondas(inst, prob_fallo=0, rondas=1, repeticiones=1)
    ronda = r["rondas"][0]
    assert ronda["candidatos"] == [1] and ronda["k_ronda"] == 1 and ronda["seleccion"]["S"] == [1]
    assert ronda["seleccion"]["llamadas_ganancia"] == 1 and ronda["exacto"]["evaluaciones"] == 1
    assert r["todas_cumplen"] and "(participan todos)" in a_texto_rondas(r)


def test_el_tope_de_cada_ronda_es_el_restante_y_el_reparto_lo_respeta():
    inst = instancia_desde_diccionario(_propio(k=2, B=4, topes=(3, 3, 3)))
    r = ejecutar_rondas(inst, prob_fallo=0, rondas=2, repeticiones=1)
    r1, r2 = r["rondas"]
    assert sum(r1["reparto"]["x"].values()) == 4 and max(r1["reparto"]["x"].values()) <= 3
    for v, x in r2["reparto"]["x"].items():
        assert x <= r1["presupuesto_restante"][v]
    assert r["todas_cumplen"]


@pytest.mark.parametrize("semilla", [0, 1, 2, 3])
def test_modo_permanente_los_candidatos_nunca_aumentan(semilla):
    inst = leer_instancia(PROFESORA)
    r = ejecutar_rondas(inst, modo="permanente", prob_fallo=0.4, semilla=semilla, rondas=5, repeticiones=1,
                        exacto=False)
    assert r["todas_cumplen"]
    rondas = r["rondas"]
    for anterior, actual in zip(rondas, rondas[1:]):
        assert set(actual["candidatos"]) <= set(anterior["candidatos"])
        assert set(anterior["caidos"]) <= set(actual["caidos"])
    assert set(rondas[-1]["caidos"]) == set().union(*(set(x["fallados"]) for x in rondas))


def test_con_la_misma_semilla_los_fallados_de_cada_ronda_coinciden_en_los_dos_modos():
    inst = leer_instancia(PROFESORA)
    t = ejecutar_rondas(inst, modo="transitorio", prob_fallo=0.5, semilla=3, rondas=4, repeticiones=1, exacto=False)
    p = ejecutar_rondas(inst, modo="permanente", prob_fallo=0.5, semilla=3, rondas=4, repeticiones=1, exacto=False)
    assert [r["fallados"] for r in t["rondas"]] == [r["fallados"] for r in p["rondas"]]
    # en transitorio un fallado puede volver; en permanente no
    vuelve = any(v in t["rondas"][i + 1]["candidatos"] for i in range(3) for v in t["rondas"][i]["fallados"])
    assert vuelve
    for i in range(3):
        assert not (set(p["rondas"][i]["fallados"]) & set(p["rondas"][i + 1]["candidatos"]))


# ---------- Cota por ronda contra OPT_r (batería aleatoria pequeña) ----------

def _bateria():
    for N in (8, 10, 12):
        for densidad in (0.3, 0.6, 1.0):
            for semilla in (1, 2, 3):
                yield N, densidad, semilla


@pytest.mark.parametrize("modo", MODOS)
@pytest.mark.parametrize("N,densidad,semilla", list(_bateria()), ids=lambda x: str(x))
def test_bateria_aleatoria_respeta_la_cota_por_ronda(modo, N, densidad, semilla):
    datos = generar_instancia_influencia(N, 3, 20, densidad, semilla)
    inst = instancia_desde_diccionario(datos, f"aleatorio_N{N}_d{densidad}_s{semilla}")
    r = ejecutar_rondas(inst, modo=modo, prob_fallo=0.3, semilla=semilla, rondas=3, repeticiones=1)
    assert r["todas_cumplen"]
    for ronda in r["rondas"]:
        k_r = ronda["k_ronda"]
        if k_r == 0:
            continue
        assert ronda["exacto"]["disponible"] and set(ronda["exacto"]["S"]) <= set(ronda["candidatos"])
        assert ronda["seleccion"]["valor"] <= ronda["exacto"]["OPT"] + 1e-9
        assert ronda["razon"] >= 1 - (1 - 1 / k_r) ** k_r - 1e-9
        assert ronda["cota"] == 1 - (1 - 1 / k_r) ** k_r


def test_la_razon_minima_de_la_bateria_queda_registrada():
    """La razón mínima observada (dato para la bitácora); cualquier cambio del voraz la movería."""
    minima = 1.0
    for N, densidad, semilla in _bateria():
        inst = instancia_desde_diccionario(generar_instancia_influencia(N, 3, 20, densidad, semilla))
        for modo in MODOS:
            r = ejecutar_rondas(inst, modo=modo, prob_fallo=0.3, semilla=semilla, rondas=3, repeticiones=1)
            minima = min([minima] + [x["razon"] for x in r["rondas"] if x["razon"] is not None])
    assert 1 - (1 - 1 / 3) ** 3 <= minima <= 1


def test_sin_exacto_disponible_la_razon_queda_vacia_y_todo_cumple():
    inst = leer_instancia(RAIZ / "casos" / "propios" / "sintetico_N320_k5.json")
    r = ejecutar_rondas(inst, prob_fallo=0, rondas=1, repeticiones=1)
    ronda = r["rondas"][0]
    assert not ronda["exacto"]["disponible"] and "C(" in ronda["exacto"]["motivo"] and ronda["razon"] is None
    assert r["todas_cumplen"] and "OPT_r no disponible" in a_texto_rondas(r)


# ---------- Verificaciones nuevas (ramas de fallo) ----------

def test_verificar_variante_b_rechaza_T_menor_que_1():
    assert verificar_variante_b(1)[0].cumple and verificar_variante_b(3)[0].cumple
    assert not verificar_variante_b(0)[0].cumple and not verificar_variante_b(-2)[0].cumple
    assert not verificar_variante_b(2.0)[0].cumple


def test_verificar_seleccion_ronda_detecta_cada_falla():
    inst = instancia_desde_diccionario(_propio())
    oraculo = inst.crear_oraculo()
    bien = verificar_seleccion_ronda([1, 2], 1, oraculo, [1], 2.0)
    assert all(v.cumple for v in bien)
    fuera = verificar_seleccion_ronda([1, 2], 1, inst.crear_oraculo(), [3], 2.0)
    assert not fuera[0].cumple
    repetido = verificar_seleccion_ronda([1, 2], 2, inst.crear_oraculo(), [1, 1], 2.0)
    assert not repetido[1].cumple
    de_mas = verificar_seleccion_ronda([1, 2], 1, inst.crear_oraculo(), [1, 2], 3.0)
    assert not de_mas[2].cumple
    valor_malo = verificar_seleccion_ronda([1, 2], 1, inst.crear_oraculo(), [1], 5.0)
    assert not valor_malo[3].cumple


def test_verificar_cota_ronda():
    assert not verificar_cota_ronda(0.70, 1.0, 3)[0].cumple     # 1 − (2/3)^3 = 19/27 ≈ 0,7037 > 0,70
    assert verificar_cota_ronda(0.71, 1.0, 3)[0].cumple
    assert verificar_cota_ronda(0.0, 0.0, 0)[0].cumple


# ---------- Rechazos y parámetros inválidos ----------

def test_T_menor_que_1_rechaza_el_caso_sin_correr():
    inst = leer_instancia(PROFESORA)
    r = ejecutar_rondas(inst, rondas=0, repeticiones=1)
    assert "rondas" not in r and not r["todas_cumplen"]
    assert any("T ≥ 1" in m for m in r["traza"]["motivo_rechazo"])


def test_entrada_que_no_cumple_se_rechaza_tambien_en_la_variante():
    inst = instancia_desde_diccionario(_propio(k=3))   # k = N
    r = ejecutar_rondas(inst, repeticiones=1)
    assert "rondas" not in r and any("k < N" in m for m in r["traza"]["motivo_rechazo"])


def test_modo_q_y_repeticiones_invalidos():
    inst = leer_instancia(PROFESORA)
    with pytest.raises(ValueError, match="modo"):
        ejecutar_rondas(inst, modo="intermitente")
    with pytest.raises(ValueError, match="probabilidad"):
        ejecutar_rondas(inst, prob_fallo=1.5)
    with pytest.raises(ValueError, match="repetici"):
        ejecutar_rondas(inst, repeticiones=0)


# ---------- Entrada: numero_rondas y el campo opcional rondas ----------

def test_la_profesora_trae_numero_rondas_3_y_se_aplica_solo_en_la_variante():
    inst = leer_instancia(PROFESORA)
    assert inst.numero_rondas() == 3
    assert ejecutar_rondas(inst, prob_fallo=0, repeticiones=1, exacto=False)["entrada"]["T"] == 3
    base = ejecutar_ronda(inst, repeticiones=1)
    assert "rondas" not in base and "T" not in base["entrada"]


def test_formato_propio_rondas_opcional():
    assert instancia_desde_diccionario(_propio()).numero_rondas() is None
    assert ejecutar_rondas(instancia_desde_diccionario(_propio()), prob_fallo=0, repeticiones=1)["entrada"]["T"] == 1
    inst = instancia_desde_diccionario(_propio(rondas=2))
    assert inst.numero_rondas() == 2
    assert len(ejecutar_rondas(inst, prob_fallo=0, repeticiones=1)["rondas"]) == 2
    assert len(ejecutar_rondas(inst, prob_fallo=0, rondas=4, repeticiones=1)["rondas"]) == 4   # --rondas manda
    for malo in ("3", 2.0, True, None):
        with pytest.raises(ErrorDeFormato, match="rondas"):
            instancia_desde_diccionario(_propio(rondas=malo))


# ---------- Caso de la docente: regresión de las evidencias ----------

def _lee(ruta):
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


@pytest.mark.parametrize("modo", MODOS)
def test_profesora_tres_rondas_q_0_2_semilla_0(modo):
    r = ejecutar_rondas(leer_instancia(PROFESORA), modo=modo, repeticiones=1)
    assert r["todas_cumplen"] and r["entrada"]["T"] == 3
    r1, r2, r3 = r["rondas"]
    assert r1["fallados"] == [] and r2["fallados"] == ["N11"] and r3["fallados"] == ["N06", "N11"]
    assert r1["seleccion"]["S"] == ["N11", "N14", "N09", "N15", "N13"]
    assert r1["reparto"]["x"] == {"N11": 5, "N14": 7, "N09": 7, "N15": 6, "N13": 5}
    assert r2["seleccion"]["S"] == ["N09", "N14", "N07", "N15", "N10"] and r2["razon"] == 1.0
    assert r3["seleccion"]["S"] == r2["seleccion"]["S"] and r3["razon"] == 1.0
    assert r3["presupuesto_restante"]["N09"] == 0 and r3["presupuesto_restante"]["N14"] == 0
    assert r3["presupuesto_restante"]["N15"] == 0 and r3["presupuesto_restante"]["N01"] == 18
    assert abs(r1["razon"] - 0.997754) < 1e-6


@pytest.mark.parametrize("modo", MODOS)
def test_las_evidencias_del_repositorio_coinciden_con_una_corrida_nueva(modo):
    guardado = _lee(EVIDENCIAS / f"b_profesora_{modo}" / "entrada_G2_red_15_nodos" / "salida.json")
    assert guardado["variante"]["modo"] == modo and guardado["todas_cumplen"]
    nuevo = ejecutar_rondas(leer_instancia(PROFESORA), modo=modo, repeticiones=1)
    for a, b in zip(guardado["rondas"], nuevo["rondas"]):
        assert a["fallados"] == b["fallados"] and a["candidatos"] == b["candidatos"]
        assert a["seleccion"]["S"] == b["seleccion"]["S"] and a["seleccion"]["valor"] == b["seleccion"]["valor"]
        assert a["exacto"]["OPT"] == b["exacto"]["OPT"] and a["reparto"]["x"] == b["reparto"]["x"]
        assert a["presupuesto_restante"] == b["presupuesto_restante"]


# ---------- ejecutar.py --variante b ----------

def test_ejecutar_con_variante_b_escribe_evidencias_y_resumen_por_ronda(tmp_path):
    salida = tmp_path / "b"
    assert main([str(PROFESORA), "--salida", str(salida), "--repeticiones", "2", "--variante", "b",
                 "--modo-fallo", "permanente", "--prob-fallo", "0.2", "--semilla-fallos", "0", "--rondas", "2"]) == 0
    datos = _lee(salida / "entrada_G2_red_15_nodos" / "salida.json")
    assert datos["variante"]["nombre"] == "b" and datos["variante"]["modo"] == "permanente"
    assert datos["entrada"]["T"] == 2 and len(datos["rondas"]) == 2 and "traza" not in datos
    assert datos["rondas"][0]["tiempos_segundos"]["repeticiones"] == 2
    traza = _lee(salida / "entrada_G2_red_15_nodos" / "traza.json")
    assert len(traza["rondas"]) == 2 and traza["rondas"][1]["fallados"] == ["N11"]
    texto = (salida / "entrada_G2_red_15_nodos" / "traza.txt").read_text(encoding="utf-8")
    assert "VARIANTE (b)" in texto and "== Ronda 2 ==" in texto and "Caídos acumulados" in texto
    with open(salida / "resumen.csv", newline="", encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    assert [f["ronda"] for f in filas] == ["1", "2"] and filas[1]["fallados"] == "N11"
    assert filas[0]["S_r"] == "N11 N14 N09 N15 N13" and filas[1]["modo"] == "permanente"
    assert filas[0]["todas_cumplen"] == "True" and filas[1]["candidatos"] == "14"


def test_ejecutar_variante_b_con_un_caso_rechazado_deja_una_fila(tmp_path):
    caso = tmp_path / "k_igual_N.json"
    caso.write_text(json.dumps(_propio(k=3)), encoding="utf-8")
    salida = tmp_path / "b"
    assert main([str(caso), "--salida", str(salida), "--repeticiones", "1", "--variante", "b"]) == 1
    with open(salida / "resumen.csv", newline="", encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    assert len(filas) == 1 and filas[0]["ronda"] == "" and filas[0]["todas_cumplen"] == "False"
    assert "Caso rechazado" in (salida / "k_igual_N" / "traza.txt").read_text(encoding="utf-8")


def test_ejecutar_sin_variante_b_no_cambia_el_resumen(tmp_path):
    salida = tmp_path / "base"
    assert main([str(PROFESORA), "--salida", str(salida), "--repeticiones", "1"]) == 0
    with open(salida / "resumen.csv", newline="", encoding="utf-8") as archivo:
        encabezado = next(csv.reader(archivo))
    assert "ronda" not in encabezado and encabezado[0] == "caso" and encabezado[-1] == "todas_cumplen"


@pytest.mark.parametrize("argumentos", [["--prob-fallo", "1.5"], ["--prob-fallo", "x"], ["--rondas", "0"],
                                        ["--modo-fallo", "intermitente"]])
def test_ejecutar_rechaza_parametros_invalidos_de_la_variante_b(tmp_path, argumentos):
    with pytest.raises(SystemExit):
        main([str(PROFESORA), "--salida", str(tmp_path), "--variante", "b"] + argumentos)
