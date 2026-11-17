"""Pruebas de scripts/experimentos.py con tamaños mínimos y pocas repeticiones (sin gráficas)."""

import importlib.util
import sys
from math import comb
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("experimentos", RAIZ / "scripts" / "experimentos.py")
experimentos = importlib.util.module_from_spec(_spec)
sys.modules["experimentos"] = experimentos
_spec.loader.exec_module(experimentos)


def test_medir_devuelve_minimo_mediana_y_conteo():
    estado = {"n": 0}

    def preparar():
        return (lambda: estado.update(n=estado["n"] + 1), lambda: 42)

    t_min, t_mediana, conteo = experimentos.medir(preparar, 5)
    assert estado["n"] == 5 and conteo == 42 and 0 <= t_min <= t_mediana


def test_conteos_coinciden_con_las_formulas_del_informe(monkeypatch):
    # selección: k·N − k(k−1)/2 llamadas; reparto: B extracciones + B inserciones; exacto: C(N, k)
    monkeypatch.setitem(experimentos.SERIES, "a", (*experimentos.SERIES["a"][:2], [20], *experimentos.SERIES["a"][3:]))
    monkeypatch.setitem(experimentos.SERIES, "d", (*experimentos.SERIES["d"][:2], [50], *experimentos.SERIES["d"][3:]))
    monkeypatch.setitem(experimentos.SERIES, "f", (*experimentos.SERIES["f"][:2], [8], *experimentos.SERIES["f"][3:]))
    fila_a = experimentos.ejecutar_serie("a", 2)[0]
    assert fila_a["conteo"] == 5 * 20 - 5 * 4 // 2
    fila_d = experimentos.ejecutar_serie("d", 2)[0]
    assert fila_d["conteo"] == 2 * 1000
    fila_f = experimentos.ejecutar_serie("f", 2)[0]
    assert fila_f["conteo"] == comb(8, 3)


def test_csv_con_las_columnas_pedidas(tmp_path, monkeypatch):
    monkeypatch.setattr(experimentos, "SALIDA", tmp_path)
    monkeypatch.setitem(experimentos.SERIES, "c", (*experimentos.SERIES["c"][:2], [25, 50], *experimentos.SERIES["c"][3:]))
    experimentos.main(["--series", "c", "--sin-graficas", "--repeticiones", "2"])
    primera = (tmp_path / "c_influencia_grado5.csv").read_text(encoding="utf-8").splitlines()[0]
    assert primera.split(",") == experimentos.COLUMNAS


def test_pendiente_recupera_un_exponente():
    from math import log
    xs = [log(n) for n in (10, 20, 40, 80)]
    assert abs(experimentos.pendiente(xs, [2 * x + 1 for x in xs]) - 2) < 1e-9


def test_ajustar_reparto_recupera_a_y_b_de_datos_exactos():
    from math import log2
    filas = [{"N": n, "B": b, "t_min": 3e-6 * n + 2e-7 * b * log2(n)}
             for n, b in [(1000, 1000), (4000, 1000), (100, 2000), (100, 8000)]]
    a, b = experimentos.ajustar_reparto(filas)
    assert abs(a - 3e-6) < 1e-12 and abs(b - 2e-7) < 1e-12
    assert all(abs(experimentos.error_relativo(f)) < 1e-9 for f in filas)


def test_serie_h_cuenta_candidatos_y_anota_las_repeticiones(monkeypatch):
    monkeypatch.setitem(experimentos.SERIES, "h", (*experimentos.SERIES["h"][:2], [12], *experimentos.SERIES["h"][3:]))
    fila = experimentos.ejecutar_serie("h", 3)[0]
    assert fila["conteo"] == 10 * (12 + 1) * (12 + 2) // 2 and fila["T_teorica"] == 10 * 12 ** 2
    assert fila["repeticiones"] == 3 and "repeticiones" in experimentos.COLUMNAS_H


def test_medir_con_limite_baja_a_5_repeticiones_si_la_primera_es_lenta():
    llamadas = []

    def preparar():
        return (lambda: llamadas.append(1), lambda: 0)

    assert experimentos.medir_con_limite(preparar, 21, limite=-1.0)[3] == 5 and len(llamadas) == 5
    llamadas.clear()
    assert experimentos.medir_con_limite(preparar, 21, limite=1e9)[3] == 21 and len(llamadas) == 21


# ------------------------------------------------ series i a m (variantes, decisiones 48 a 53)

def _con_tamanos(monkeypatch, clave, tamanos):
    """Deja la serie `clave` con tamaños mínimos para la prueba."""
    monkeypatch.setitem(experimentos.SERIES, clave,
                        (*experimentos.SERIES[clave][:2], tamanos, *experimentos.SERIES[clave][3:]))


def test_serie_i_cuenta_el_peor_caso_exacto_del_cociente_y_del_modificado(monkeypatch):
    # L = 5N ≥ Σ c: todo cabe siempre, evaluaciones = 1 + N(N + 1)/2 (ficha de variante_costos)
    for clave in ("ic", "im"):
        _con_tamanos(monkeypatch, clave, [12, 20])
        for fila in experimentos.ejecutar_serie(clave, 2):
            n = fila["N"]
            assert fila["conteo"] == 1 + n * (n + 1) // 2 and fila["L"] == 5 * n
            assert fila["T_teorica"] == n * n * (1 + 2 * fila["A"] / n)


def test_serie_i_el_conteo_es_el_de_los_contadores_del_oraculo():
    inst, p = experimentos._instancia_costos(15)
    assert p["L"] >= sum(inst.costos().values())
    oraculo = inst.crear_oraculo()
    r = experimentos.voraz_modificado(oraculo, inst.ids(), inst.costos(), p["L"])
    assert r.evaluaciones == oraculo.llamadas_ganancia + oraculo.llamadas_valor == 1 + 15 * 16 // 2


def test_serie_j_cuenta_las_evaluaciones_del_peor_caso_de_la_enumeracion(monkeypatch):
    _con_tamanos(monkeypatch, "j", [8, 9])
    for fila in experimentos.ejecutar_serie("j", 1):
        n = fila["N"]
        esperado = 1 + n + comb(n, 2) + comb(n, 3) * (1 + (n - 3) * (n - 2) // 2)
        assert fila["conteo"] == esperado
        assert abs(fila["T_teorica"] - esperado * (1 + 2 * fila["A"] / n)) < 1e-9


def test_serie_k_evalua_los_2_a_la_N_subconjuntos(monkeypatch):
    _con_tamanos(monkeypatch, "k", [8, 10])
    for fila in experimentos.ejecutar_serie("k", 1):
        assert fila["conteo"] == 2 ** fila["N"]
        assert fila["T_teorica"] == 2 ** fila["N"] * (fila["N"] + fila["A"])


def test_serie_l_cuenta_las_llamadas_de_cada_ronda_y_el_restante_no_se_agota():
    preparar, resultado = experimentos._preparar_rondas(experimentos.instancia_rondas(), 6,
                                                        experimentos.Q_RONDAS, experimentos.SEMILLA)
    ejecutar, contar = preparar()
    ejecutar()
    rondas = resultado[0]["rondas"]
    esperado = sum(r["k_ronda"] * len(r["candidatos"]) - r["k_ronda"] * (r["k_ronda"] - 1) // 2 for r in rondas)
    assert len(rondas) == 6 and contar() == esperado
    assert all(r["k_ronda"] == experimentos.K_RONDAS for r in rondas)       # cada ronda con k completo
    assert all(r["exacto"]["disponible"] is False for r in rondas)          # el exacto no corre en el reloj
    tope = experimentos.B_RONDAS * experimentos.MAXIMO_RONDAS
    assert all(v >= tope - experimentos.B_RONDAS * 6 > 0 for v in rondas[-1]["presupuesto_restante"].values())
    assert resultado[0]["todas_cumplen"]


def test_serie_l_teorica_lineal_en_T(monkeypatch):
    _con_tamanos(monkeypatch, "l", [2, 4])
    filas = experimentos.ejecutar_serie("l", 1)
    assert abs(filas[1]["T_teorica"] - 2 * filas[0]["T_teorica"]) < 1e-9
    assert [f["n"] for f in filas] == [2, 4] and filas[0]["q"] == 0.2 and filas[0]["modo"] == "transitorio"


def test_serie_m_cuenta_m_mas_B_por_m_ganancias_con_S_completo(monkeypatch):
    # S completo y nadie en su tope: m + B·m ganancias recalculadas y B·m revisados (ficha de variante_vecinos)
    _con_tamanos(monkeypatch, "m", [30, 60])
    for fila in experimentos.ejecutar_serie("m", 2):
        m, b = fila["k"], fila["B"]
        assert m == experimentos.K_C2 and fila["A_S"] == m * (m - 1) // 2
        assert fila["conteo"] == m + b * m
        assert fila["T_teorica"] == m + fila["d_S"] + b * (m + fila["A_S"])
    preparar, resultado = experimentos._preparar_c2(["N01", "N02", "N03"], 7, {"N01": 1, "N02": 2, "N03": 3},
                                                    {"N01": {"N02": 0.5, "N03": 0.5}, "N02": {"N01": 0.5, "N03": 0.5},
                                                     "N03": {"N01": 0.5, "N02": 0.5}}, 0.2)
    ejecutar, contar = preparar()
    ejecutar()
    assert contar() == 3 + 7 * 3 and resultado[0].revisados == 7 * 3


def test_alias_i_y_columnas_de_las_series_nuevas(tmp_path, monkeypatch):
    assert experimentos.expandir_series(["i", "j", "ic"]) == ["ic", "im", "j"]
    monkeypatch.setattr(experimentos, "SALIDA", tmp_path)
    for clave in ("ic", "im", "m"):
        _con_tamanos(monkeypatch, clave, [10, 12] if clave != "m" else [20, 40])
    experimentos.main(["--series", "i", "m", "--sin-graficas", "--repeticiones", "1"])
    for clave in ("ic", "im", "m"):
        nombre = experimentos.SERIES[clave][0]
        primera = (tmp_path / f"{nombre}.csv").read_text(encoding="utf-8").splitlines()[0]
        assert primera.split(",") == experimentos.COLUMNAS + experimentos.COLUMNAS_EXTRA[clave]
    assert sorted(p.name for p in tmp_path.iterdir()) == ["i_costos_cociente.csv", "i_costos_modificado.csv",
                                                           "m_c2_varia_B.csv"]


def test_las_series_a_h_no_cambian_de_columnas():
    assert experimentos.columnas_de("a") == experimentos.COLUMNAS
    assert experimentos.columnas_de("h") == experimentos.COLUMNAS_H
    assert experimentos.columnas_de("d", True) == experimentos.COLUMNAS_AJUSTADAS
    assert experimentos.columnas_de("d", False) == experimentos.COLUMNAS
