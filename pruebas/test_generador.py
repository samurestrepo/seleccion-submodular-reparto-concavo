"""Pruebas de generador.py: la ayuda en consolas Windows y la instancia guardada en casos/propios."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

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


# ---------------------------------------------------------------- formato de influencia (P-2)
import json  # noqa: E402

from red.entrada import leer_instancia  # noqa: E402
from red.generador import generar_instancia_influencia, main as main_generador  # noqa: E402


def test_influencia_misma_semilla_misma_instancia():
    assert generar_instancia_influencia(12, 3, 20, 0.4, 7) == generar_instancia_influencia(12, 3, 20, 0.4, 7)
    assert generar_instancia_influencia(12, 3, 20, 0.4, 7) != generar_instancia_influencia(12, 3, 20, 0.4, 8)


def test_influencia_densidad_1_da_todas_las_aristas_no_dirigidas():
    # el grafo del formato de la profesora no es dirigido: {u, v} y {v, u} son la misma arista
    N = 9
    assert len(generar_instancia_influencia(N, 3, 10, 1, 1)["grafo"]) == N * (N - 1) // 2


def test_influencia_densidad_0_no_da_aristas():
    assert generar_instancia_influencia(9, 3, 10, 0, 1)["grafo"] == []


def test_influencia_rangos_y_ids():
    datos = generar_instancia_influencia(120, 5, 30, 0.1, 3)
    assert datos["nodos"][0]["id"] == "N001" and datos["nodos"][-1]["id"] == "N120"
    assert generar_instancia_influencia(15, 5, 30, 0.1, 3)["nodos"][0]["id"] == "N01"
    assert datos["parametros"]["numero_rondas"] == 1
    assert all(0.05 <= a["peso_influencia"] <= 0.70 for a in datos["grafo"])
    assert all(1 <= n["coeficiente_utilidad"] <= 10 and 1 <= n["costo_participacion"] <= 5
               for n in datos["nodos"])


@pytest.mark.parametrize("densidad", [0, 0.3, 1])
def test_influencia_pasa_leer_instancia_y_las_verificaciones(tmp_path, densidad):
    from red.verificacion import verificar_entrada
    ruta = tmp_path / "caso.json"
    main_generador(["--N", "20", "--k", "4", "--B", "15", "--formato", "influencia",
                    "--densidad", str(densidad), "--semilla", "2", "--salida", str(ruta)])
    instancia = leer_instancia(ruta)
    assert instancia.N == 20 and instancia.k == 4 and instancia.B == 15
    assert all(v.cumple for v in verificar_entrada(instancia))
    assert json.loads(ruta.read_text(encoding="utf-8"))["parametros"]["numero_nodos"] == 20


def test_influencia_rechaza_parametros_malos():
    with pytest.raises(ValueError):
        generar_instancia_influencia(5, 5, 10, 0.5)
    with pytest.raises(ValueError):
        generar_instancia_influencia(5, 2, 10, 1.5)
