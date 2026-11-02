"""Pruebas directas de traza.py: lo que anota, los archivos y el reporte de un caso rechazado."""

import json

from red.entrada import Instancia, Nodo
from red.ronda import ejecutar_ronda, resultado_de_error
from red.traza import Traza, a_texto, escribir_json
from red.utilidades import UtilidadLog, UtilidadTabla


def test_traza_anota_los_pasos_y_las_unidades():
    traza = Traza()
    traza.paso_seleccion(1, [(1, 3), (2, 2)], 1, 3, 3)
    traza.unidad_reparto(1, 1, 9)
    assert traza.a_diccionario() == {
        "pasos_seleccion": [{
            "paso": 1,
            "aportes": [{"nodo": 1, "ganancia": 3}, {"nodo": 2, "ganancia": 2}],
            "elegido": 1,
            "ganancia_elegido": 3,
            "valor_despues": 3,
        }],
        "unidades_reparto": [{"unidad": 1, "nodo": 1, "ganancia": 9}],
    }


def test_motivo_de_rechazo_solo_aparece_si_hubo_rechazo():
    traza = Traza()
    assert "motivo_rechazo" not in traza.a_diccionario()
    traza.entrada_rechazada(["k = N"])
    assert traza.a_diccionario()["motivo_rechazo"] == ["k = N"]


def test_escribir_json_conserva_los_acentos(tmp_path):
    ruta = tmp_path / "datos.json"
    escribir_json(ruta, {"nombre": "selección Δ"})
    assert "selección Δ" in ruta.read_text(encoding="utf-8")
    assert json.loads(ruta.read_text(encoding="utf-8")) == {"nombre": "selección Δ"}


def test_a_texto_de_una_ronda_valida():
    nodos = [Nodo(1, ["a", "b"], UtilidadTabla([1.5])), Nodo(2, ["c"], UtilidadLog(1.0))]
    texto = a_texto(ejecutar_ronda(Instancia(1, 1, nodos, "valida")))
    assert "CASO: valida" in texto
    assert "Paso 1: Δ(1) = 2, Δ(2) = 1" in texto
    assert "Unidad 1: al nodo 1 (Δ = 1.5000)" in texto
    assert "TODAS LAS VERIFICACIONES: CUMPLEN" in texto


def test_a_texto_de_una_entrada_invalida_no_falla():
    # H2: antes lanzaba KeyError: 'traza'
    nodos = [Nodo(1, [], UtilidadLog(1.0)), Nodo(2, [], UtilidadLog(1.0))]
    texto = a_texto(ejecutar_ronda(Instancia(2, 1, nodos, "invalida")))
    assert "N = 2, k = 2, B = 1" in texto
    assert "[FALLA] 1 ≤ k < N: k = 2, N = 2" in texto
    assert "Motivo: 1 ≤ k < N: k = 2, N = 2" in texto
    assert "TODAS LAS VERIFICACIONES: HAY FALLAS" in texto


def test_a_texto_de_un_archivo_que_no_se_pudo_leer():
    texto = a_texto(resultado_de_error("malo", "no es un JSON válido"))
    assert "N, k y B: no se pudieron leer del archivo" in texto
    assert "Motivo: archivo legible y con la forma esperada: no es un JSON válido" in texto
