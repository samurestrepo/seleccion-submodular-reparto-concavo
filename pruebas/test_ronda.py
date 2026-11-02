import json

from ejecutar import main
from red.entrada import instancia_desde_diccionario, leer_instancia
from red.generador import generar_instancia
from red.ronda import ejecutar_ronda


def test_ronda_del_ejemplo_del_informe():
    r = ejecutar_ronda(leer_instancia("casos/propios/ejemplo_informe.json"))
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
    codigo = main(["casos/propios/ejemplo_informe.json", "--salida", str(tmp_path)])
    assert codigo == 0
    carpeta = tmp_path / "ejemplo_informe"
    for archivo in ("salida.json", "traza.json", "traza.txt"):
        assert (carpeta / archivo).exists()
    salida = json.loads((carpeta / "salida.json").read_text(encoding="utf-8"))
    assert salida["todas_cumplen"]
    assert (tmp_path / "resumen.csv").exists()
