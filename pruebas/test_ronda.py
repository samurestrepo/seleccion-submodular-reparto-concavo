import json
from pathlib import Path

import pytest

from ejecutar import main
from red import ronda
from red.entrada import instancia_desde_diccionario, leer_instancia
from red.generador import generar_instancia
from red.ronda import REPETICIONES, _resumen_tiempos, ejecutar_ronda
from red.traza import a_texto

EJEMPLO = Path(__file__).resolve().parent.parent / "casos" / "propios" / "ejemplo_informe.json"


def test_ronda_del_ejemplo_del_informe():
    r = ejecutar_ronda(leer_instancia(EJEMPLO))
    assert r["todas_cumplen"]
    assert r["seleccion"]["S"] == [1, 3]
    assert r["seleccion"]["valor"] == 5
    assert r["seleccion"]["llamadas_ganancia"] == 2 * 3 - 1
    assert sum(r["reparto"]["x"].values()) == 4
    assert set(r["reparto"]["x"]) == {"1", "3"}


def test_entrada_invalida_no_corre_los_algoritmos():
    datos = {"k": 3, "B": 2, "nodos": [  # k = N: no cumple k < N
        {"id": i, "cubre": ["a"], "utilidad": {"tipo": "log", "a": 1}} for i in (1, 2, 3)]}
    r = ejecutar_ronda(instancia_desde_diccionario(datos))
    assert not r["todas_cumplen"]
    assert "seleccion" not in r
    assert r["traza"]["motivo_rechazo"] == ["1 ≤ k < N: k = 3, N = 3"]
    assert r["traza"]["pasos_seleccion"] == []


def test_ronda_con_tabla_mala_fuera_del_presupuesto_corre_y_es_optima():
    # H10: Δ(2) = 5 nunca se entrega con B = 2, así que el caso es válido
    datos = {"k": 1, "B": 2, "nodos": [
        {"id": 1, "cubre": ["a", "b"], "utilidad": {"tipo": "tabla", "ganancias": [3, 2, 5]}},
        {"id": 2, "cubre": ["c"], "utilidad": {"tipo": "log", "a": 1}}]}
    r = ejecutar_ronda(instancia_desde_diccionario(datos))
    assert r["todas_cumplen"]
    assert r["reparto"]["x"] == {"1": 2}
    assert r["reparto"]["utilidad"] == 5


def test_utilidad_no_concava_se_reporta():
    datos = {"k": 1, "B": 2, "nodos": [
        {"id": 1, "cubre": ["a"], "utilidad": {"tipo": "tabla", "ganancias": [1, 10]}},
        {"id": 2, "cubre": ["b"], "utilidad": {"tipo": "log", "a": 1}}]}
    r = ejecutar_ronda(instancia_desde_diccionario(datos))
    falla = [v for v in r["verificaciones"]["entrada"] if not v["cumple"]]
    assert len(falla) == 1 and "cóncava" in falla[0]["detalle"]


def test_generador_reproducible_y_valido():
    a = generar_instancia(30, 4, 50, semilla=11)
    b = generar_instancia(30, 4, 50, semilla=11)
    assert a == b
    r = ejecutar_ronda(instancia_desde_diccionario(a))
    assert r["todas_cumplen"]
    assert len(r["seleccion"]["S"]) == 4


def test_ejecutar_escribe_las_evidencias(tmp_path):
    codigo = main([str(EJEMPLO), "--salida", str(tmp_path)])
    assert codigo == 0
    carpeta = tmp_path / "ejemplo_informe"
    for archivo in ("salida.json", "traza.json", "traza.txt"):
        assert (carpeta / archivo).exists()
    salida = json.loads((carpeta / "salida.json").read_text(encoding="utf-8"))
    assert salida["todas_cumplen"]
    assert (tmp_path / "resumen.csv").exists()


def caso_profesora_pequeno(costos=(3, 4, 5), presupuesto_costos=9):
    """Formato de la profesora con 3 nodos, k = 2 y B = 4."""
    return {
        "parametros": {"numero_nodos": 3, "numero_rondas": 7, "cupo_participantes_por_ronda_k": 2,
                       "presupuesto_ruido_por_ronda_B": 4,
                       "presupuesto_costos_participacion_por_ronda": presupuesto_costos},
        "grafo": [{"u": "N1", "v": "N2", "peso_influencia": 0.5},
                  {"u": "N2", "v": "N3", "peso_influencia": 0.2}],
        "nodos": [{"id": f"N{i}", "coeficiente_utilidad": 2.0, "presupuesto_total_nodo": 18,
                   "costo_participacion": costos[i - 1]} for i in (1, 2, 3)],
    }


def test_informativo_del_formato_de_la_profesora():
    r = ejecutar_ronda(instancia_desde_diccionario(caso_profesora_pequeno()))
    assert r["todas_cumplen"]
    S = r["seleccion"]["S"]
    costos = {"N1": 3, "N2": 4, "N3": 5}
    assert r["informativo"] == {
        "variante_a": {"suma_costos_de_S": sum(costos[v] for v in S),
                       "presupuesto_costos_participacion_por_ronda": 9,
                       "nota": "no se aplica en la solución base"},
        "variante_b": {"numero_rondas": 7, "nota": "no se aplica en la solución base"},
    }
    texto = a_texto(r)
    assert "== Informativo" in texto
    assert "numero_rondas = 7" in texto
    assert texto.count("no se aplica en la solución base") == 2


def test_informativo_no_es_una_verificacion_ni_decide_todas_cumplen():
    # Los costos de S superan por mucho al presupuesto de costos, y aun así todo cumple
    datos = caso_profesora_pequeno(costos=(100, 100, 100), presupuesto_costos=1)
    r = ejecutar_ronda(instancia_desde_diccionario(datos))
    assert r["informativo"]["variante_a"]["suma_costos_de_S"] == 200
    assert r["todas_cumplen"]
    assert "informativo" not in r["verificaciones"]
    nombres = [v["nombre"] for lista in r["verificaciones"].values() for v in lista]
    assert not any("costo" in nombre or "rondas" in nombre for nombre in nombres)


def test_el_formato_propio_no_tiene_informativo():
    r = ejecutar_ronda(leer_instancia(EJEMPLO))
    assert "informativo" not in r
    assert "Informativo" not in a_texto(r)


def test_un_caso_de_la_profesora_rechazado_no_tiene_informativo_y_su_texto_no_falla():
    # k = N: no hay S del cual sumar costos
    datos = caso_profesora_pequeno()
    datos["parametros"]["cupo_participantes_por_ronda_k"] = 3
    r = ejecutar_ronda(instancia_desde_diccionario(datos))
    assert "seleccion" not in r
    assert "informativo" not in r
    assert "Caso rechazado" in a_texto(r)


def test_presupuesto_total_nodo_es_el_tope():
    # Decisión 28: con presupuesto_total_nodo = 1, k = 2 y B = 4 solo se pueden gastar 2 unidades
    datos = caso_profesora_pequeno()
    for nodo in datos["nodos"]:
        nodo["presupuesto_total_nodo"] = 1
    r = ejecutar_ronda(instancia_desde_diccionario(datos))
    assert sorted(r["reparto"]["x"].values()) == [1, 1]
    assert (r["reparto"]["extracciones"], r["reparto"]["inserciones"]) == (2, 0)
    assert r["todas_cumplen"]                 # sobrar presupuesto no es una falla
    nombres = [v["nombre"] for v in r["verificaciones"]["reparto"]]
    assert "cada x_i ≤ c_i" in nombres


def test_formato_propio_sin_tope_gasta_todo_B():
    r = ejecutar_ronda(leer_instancia(EJEMPLO))
    assert sum(r["reparto"]["x"].values()) == 4
    assert (r["reparto"]["extracciones"], r["reparto"]["inserciones"]) == (4, 4)
    assert "cada x_i ≤ c_i" not in [v["nombre"] for v in r["verificaciones"]["reparto"]]


# ---- Mediana de repeticiones ----

def test_tiempos_reportan_mediana_minimo_maximo_y_R():
    r = ejecutar_ronda(leer_instancia(EJEMPLO), repeticiones=5)
    t = r["tiempos_segundos"]
    assert t["repeticiones"] == 5
    for parte in ("seleccion", "reparto"):
        assert t[parte]["minimo"] <= t[parte]["mediana"] <= t[parte]["maximo"]


def test_por_omision_son_21_repeticiones():
    assert REPETICIONES == 21
    assert ejecutar_ronda(leer_instancia(EJEMPLO))["tiempos_segundos"]["repeticiones"] == 21


def test_la_mediana_no_se_deja_arrastrar_por_una_repeticion_lenta():
    assert _resumen_tiempos([1.0, 2.0, 1000.0]) == {"mediana": 2.0, "minimo": 1.0, "maximo": 1000.0}
    assert _resumen_tiempos([5.0]) == {"mediana": 5.0, "minimo": 5.0, "maximo": 5.0}


def test_cada_repeticion_corre_los_dos_algoritmos_con_un_oraculo_nuevo(monkeypatch):
    # R repeticiones medidas más la ejecución con traza
    oraculos = []
    repartos = []
    seleccion_real = ronda.seleccionar_nodos
    reparto_real = ronda.repartir_presupuesto

    def seleccion_espia(oraculo, V, k, traza=None):
        assert oraculo.llamadas_ganancia == 0     # contadores en cero: el oráculo es nuevo
        oraculos.append(oraculo)
        return seleccion_real(oraculo, V, k, traza)

    def reparto_espia(*argumentos, **opciones):
        repartos.append(argumentos)
        return reparto_real(*argumentos, **opciones)

    monkeypatch.setattr(ronda, "seleccionar_nodos", seleccion_espia)
    monkeypatch.setattr(ronda, "repartir_presupuesto", reparto_espia)
    r = ronda.ejecutar_ronda(leer_instancia(EJEMPLO), repeticiones=7)
    assert len(oraculos) == len(set(map(id, oraculos))) == 8
    assert len(repartos) == 8
    # El conteo que se reporta y se verifica es el de la primera repetición, no la suma
    assert r["seleccion"]["llamadas_ganancia"] == 5
    assert r["todas_cumplen"]


def test_una_repeticion_con_otro_S_se_detecta(monkeypatch):
    real = ronda.seleccionar_nodos
    llamadas = []

    def seleccion_inestable(oraculo, V, k, traza=None):
        llamadas.append(1)
        S, valor = real(oraculo, V, k, traza)
        return (list(reversed(S)), valor) if len(llamadas) == 3 else (S, valor)

    monkeypatch.setattr(ronda, "seleccionar_nodos", seleccion_inestable)
    r = ronda.ejecutar_ronda(leer_instancia(EJEMPLO), repeticiones=5)
    assert not r["todas_cumplen"]
    falla = [v for v in r["verificaciones"]["ejecucion"] if not v["cumple"]]
    assert [v["nombre"] for v in falla] == ["todas las repeticiones dan el mismo S y el mismo reparto"]
    assert "[3]" in falla[0]["detalle"]


def test_lo_reportado_es_la_primera_repeticion(monkeypatch):
    # La última sale distinta: se detecta, y lo que queda en el resultado sigue siendo la primera
    real = ronda.seleccionar_nodos
    llamadas = []

    def seleccion_inestable(oraculo, V, k, traza=None):
        llamadas.append(1)
        S, valor = real(oraculo, V, k, traza)
        return (list(reversed(S)), valor) if len(llamadas) == 3 else (S, valor)

    monkeypatch.setattr(ronda, "seleccionar_nodos", seleccion_inestable)
    r = ronda.ejecutar_ronda(leer_instancia(EJEMPLO), repeticiones=3)
    assert r["seleccion"]["S"] == [1, 3]
    assert not r["todas_cumplen"]


def test_una_repeticion_con_otro_reparto_se_detecta(monkeypatch):
    real = ronda.repartir_presupuesto
    llamadas = []

    def reparto_inestable(*argumentos, **opciones):
        llamadas.append(1)
        resultado = real(*argumentos, **opciones)
        if len(llamadas) == 2:
            resultado.x = {i: 0 for i in resultado.x}
        return resultado

    monkeypatch.setattr(ronda, "repartir_presupuesto", reparto_inestable)
    r = ronda.ejecutar_ronda(leer_instancia(EJEMPLO), repeticiones=3)
    assert not r["todas_cumplen"]
    assert "[2]" in r["verificaciones"]["ejecucion"][0]["detalle"]


def test_una_sola_repeticion_tambien_funciona():
    r = ejecutar_ronda(leer_instancia(EJEMPLO), repeticiones=1)
    assert r["todas_cumplen"]
    t = r["tiempos_segundos"]
    assert t["seleccion"]["minimo"] == t["seleccion"]["mediana"] == t["seleccion"]["maximo"]


@pytest.mark.parametrize("repeticiones", [0, -1])
def test_repeticiones_menor_que_uno_es_un_error(repeticiones):
    with pytest.raises(ValueError):
        ejecutar_ronda(leer_instancia(EJEMPLO), repeticiones=repeticiones)


def test_un_caso_rechazado_no_tiene_tiempos():
    datos = caso_profesora_pequeno()
    datos["parametros"]["cupo_participantes_por_ronda_k"] = 3
    assert "tiempos_segundos" not in ejecutar_ronda(instancia_desde_diccionario(datos))


def test_la_traza_dice_cuantas_repeticiones_midio():
    texto = a_texto(ejecutar_ronda(leer_instancia(EJEMPLO), repeticiones=3))
    assert "mediana de 3 repeticiones" in texto


def test_los_oraculos_de_la_ronda_estan_separados():
    # Si compartieran contador, las llamadas no darían k·N − k(k−1)/2 = 5 ni llamadas_valor = 1
    r = ejecutar_ronda(instancia_desde_diccionario(caso_profesora_pequeno()))
    assert r["seleccion"]["llamadas_ganancia"] == 5
    assert r["seleccion"]["llamadas_valor"] == 1
