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
