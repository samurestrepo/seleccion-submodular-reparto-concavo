"""Prueba fuera de muestra de la serie d (P-6 fase 1, decisión 60).

Lee los CSV de resultados/experimentos/ del repositorio (no mide nada) y comprueba los valores que
cita el informe final (sección 11.3, punto 2): a, b, el error por punto y las dos pendientes; que el
CSV guardado coincide con lo calculado; y que --help no lee ni escribe nada.
"""

import csv
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "serie_d_fuera_de_muestra.py"
CSV = RAIZ / "resultados" / "experimentos" / "d_fuera_de_muestra.csv"
ERRORES_DEL_INFORME = {1000: -0.002, 2000: 0.018, 4000: -0.055, 8000: -0.182, 16000: -0.359}


def _cargar():
    """Importa el script como módulo (scripts/ no es un paquete); importarlo no ejecuta main."""
    spec = importlib.util.spec_from_file_location("serie_d_fuera_de_muestra", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture(scope="module")
def resultado():
    return _cargar().calcular()


def test_constantes_a_y_b(resultado):
    r = resultado["resumen"]
    assert r["a_s"] == pytest.approx(7.98e-7, abs=0.005e-7)
    assert r["b_s"] == pytest.approx(1.99e-7, abs=0.005e-7)


def test_error_por_punto(resultado):
    errores = {p["N"]: p["error_relativo"] for p in resultado["puntos"]}
    assert set(errores) == set(ERRORES_DEL_INFORME)
    for N, esperado in ERRORES_DEL_INFORME.items():
        assert errores[N] == pytest.approx(esperado, abs=0.0005), N   # redondeo a una décima de %
    assert all(p["B"] == 1000 for p in resultado["puntos"])


def test_pendientes(resultado):
    assert resultado["resumen"]["pendiente_predicha"] == pytest.approx(0.62, abs=0.005)
    assert resultado["resumen"]["pendiente_medida"] == pytest.approx(0.78, abs=0.005)


def test_recupera_a_y_b_de_datos_exactos(tmp_path):
    """Con tiempos generados por el mismo modelo, la recta de e devuelve a y b y el error es 0."""
    modulo = _cargar()
    a, b = 3e-7, 2e-7
    for nombre, filas in (("e.csv", [(100, B) for B in (1000, 2000, 4000)]),
                          ("d.csv", [(N, 1000) for N in (1000, 4000, 16000)])):
        with open(tmp_path / nombre, "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["N", "B", "t_min"])
            for N, B in filas:
                escritor.writerow([N, B, a * N + b * B * modulo.log2(N)])
    calculado = modulo.calcular(tmp_path / "e.csv", tmp_path / "d.csv")
    assert calculado["resumen"]["a_s"] == pytest.approx(a)
    assert calculado["resumen"]["b_s"] == pytest.approx(b)
    assert all(abs(p["error_relativo"]) < 1e-9 for p in calculado["puntos"])


def test_serie_e_con_varios_N_se_rechaza():
    with pytest.raises(ValueError):
        _cargar().constantes_desde_e([{"N": 100, "B": 1000, "t_min": 1.0},
                                      {"N": 200, "B": 2000, "t_min": 2.0}])


def test_el_csv_del_repositorio_coincide_con_lo_calculado(resultado, tmp_path):
    nuevo = tmp_path / "d_fuera_de_muestra.csv"
    _cargar().escribir_csv(nuevo, resultado)
    # Se compara el texto línea por línea: git puede guardar el CSV con LF y sacarlo con CRLF.
    assert nuevo.read_text(encoding="utf-8").splitlines() == CSV.read_text(encoding="utf-8").splitlines()


@pytest.mark.parametrize("opcion", ["--help", "-h"])
def test_ayuda_por_consola_no_escribe_el_csv(opcion):
    antes = (CSV.read_bytes(), CSV.stat().st_mtime_ns)
    entorno = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONDONTWRITEBYTECODE="1")
    proceso = subprocess.run([sys.executable, str(SCRIPT), opcion], cwd=RAIZ, env=entorno,
                             capture_output=True, timeout=60)
    assert proceso.returncode == 0, proceso.stderr
    ayuda = proceso.stdout.decode("cp1252")
    assert "serie_d_fuera_de_muestra.py" in ayuda
    assert "Escrito:" not in ayuda                  # main no llegó a calcular
    assert (CSV.read_bytes(), CSV.stat().st_mtime_ns) == antes


def test_main_con_help_no_lee_ni_escribe(monkeypatch, capsys):
    modulo = _cargar()

    def prohibido(*_args, **_kwargs):
        raise AssertionError("--help no debe leer ni escribir nada")

    for nombre in ("calcular", "escribir_csv", "leer_serie"):
        monkeypatch.setattr(modulo, nombre, prohibido)
    with pytest.raises(SystemExit) as salida:
        modulo.main(["--help"])
    assert salida.value.code == 0
    capsys.readouterr().out.encode("cp1252")        # no lleva caracteres fuera de cp1252


def test_argumento_desconocido_es_error_de_uso(monkeypatch):
    modulo = _cargar()
    monkeypatch.setattr(modulo, "escribir_csv", lambda *a, **k: pytest.fail("no debe escribir"))
    with pytest.raises(SystemExit) as salida:
        modulo.main(["--otra"])
    assert salida.value.code == 2
