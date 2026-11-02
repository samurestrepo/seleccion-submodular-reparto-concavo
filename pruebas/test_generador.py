"""Pruebas de generador.py: la ayuda en consolas Windows y la instancia guardada en casos/propios."""

import json
import os
import subprocess
import sys
from pathlib import Path

from red.generador import generar_instancia

RAIZ = Path(__file__).resolve().parent.parent


def test_ayuda_se_puede_imprimir_en_cp1252():
    # H17: el símbolo "menor o igual" no existe en cp1252 y --help terminaba con UnicodeEncodeError
    entorno = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONDONTWRITEBYTECODE="1")
    proceso = subprocess.run([sys.executable, "-m", "red.generador", "--help"], cwd=RAIZ, env=entorno,
                             capture_output=True)
    assert proceso.returncode == 0, proceso.stderr


def test_semilla_reproduce_el_caso_guardado():
    guardado = json.loads((RAIZ / "casos" / "propios" / "sintetico_N040_k5.json").read_text(encoding="utf-8"))
    assert generar_instancia(40, 5, 80, semilla=1) == guardado


def test_coeficientes_generados_cumplen_a_mayor_que_cero():
    instancia = generar_instancia(200, 5, 10, semilla=3)
    assert all(nodo["utilidad"]["a"] > 0 for nodo in instancia["nodos"])
