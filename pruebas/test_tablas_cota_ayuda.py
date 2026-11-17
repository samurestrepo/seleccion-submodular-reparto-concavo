"""--help y -h de scripts/tabla_cota_variante_a.py y tabla_cota_variante_c.py (P-5, decisión 59).

Comprueba que la ayuda sale con código 0, se imprime en cp1252 (la consola de Windows) y no
calcula ni escribe el CSV: por subprocess (el CSV del repositorio no cambia ni en bytes ni en fecha)
y llamando a main con la escritura reemplazada por una función que falla si se la llama.
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
SCRIPTS = {
    "a": (RAIZ / "scripts" / "tabla_cota_variante_a.py", RAIZ / "resultados" / "variantes" / "a_tabla_cota.csv"),
    "c": (RAIZ / "scripts" / "tabla_cota_variante_c.py", RAIZ / "resultados" / "variantes" / "c_tabla_cota.csv"),
}


def _cargar(variante):
    """Importa el script como módulo (scripts/ no es un paquete); importarlo no ejecuta main."""
    ruta = SCRIPTS[variante][0]
    spec = importlib.util.spec_from_file_location(f"tabla_cota_variante_{variante}_ayuda", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.mark.parametrize("opcion", ["--help", "-h"])
@pytest.mark.parametrize("variante", ["a", "c"])
def test_ayuda_por_consola_sale_con_0_y_no_toca_el_csv(variante, opcion):
    script, csv = SCRIPTS[variante]
    antes = (csv.read_bytes(), csv.stat().st_mtime_ns)
    entorno = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONDONTWRITEBYTECODE="1")
    proceso = subprocess.run([sys.executable, str(script), opcion], cwd=RAIZ, env=entorno,
                             capture_output=True, timeout=60)
    assert proceso.returncode == 0, proceso.stderr
    ayuda = proceso.stdout.decode("cp1252")
    assert f"tabla_cota_variante_{variante}.py" in ayuda
    assert f"{variante}_tabla_cota.csv" in ayuda
    assert "filas escritas" not in ayuda            # main no llegó a correr la batería
    assert (csv.read_bytes(), csv.stat().st_mtime_ns) == antes


@pytest.mark.parametrize("variante", ["a", "c"])
def test_main_con_help_no_llama_a_la_escritura(variante, monkeypatch, capsys):
    modulo = _cargar(variante)

    def prohibido(*_args, **_kwargs):
        raise AssertionError("--help no debe calcular ni escribir nada")

    for nombre in ("escribir_csv", "bateria_aleatoria", "bateria", "fila_de_la_profesora"):
        if hasattr(modulo, nombre):
            monkeypatch.setattr(modulo, nombre, prohibido)
    with pytest.raises(SystemExit) as salida:
        modulo.main(["--help"])
    assert salida.value.code == 0
    ayuda = capsys.readouterr().out
    assert "usage" in ayuda
    ayuda.encode("cp1252")                          # no lleva caracteres fuera de cp1252


@pytest.mark.parametrize("variante", ["a", "c"])
def test_sin_argumentos_no_hay_opciones_que_leer(variante):
    modulo = _cargar(variante)
    assert vars(modulo.leer_argumentos([])) == {}


@pytest.mark.parametrize("variante", ["a", "c"])
def test_argumento_desconocido_es_error_de_uso(variante, monkeypatch, capsys):
    modulo = _cargar(variante)
    monkeypatch.setattr(modulo, "escribir_csv", lambda *a, **k: pytest.fail("no debe escribir"))
    with pytest.raises(SystemExit) as salida:
        modulo.main(["--otra"])
    assert salida.value.code == 2
