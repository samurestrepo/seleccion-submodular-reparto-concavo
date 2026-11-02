import json
from pathlib import Path

import pytest

from red.entrada import ErrorDeFormato, instancia_desde_diccionario, leer_instancia, nombre_del_caso

RAIZ = Path(__file__).resolve().parent.parent


def test_lee_el_ejemplo_del_informe():
    inst = leer_instancia(RAIZ / "casos" / "propios" / "ejemplo_informe.json")
    assert inst.nombre == "ejemplo_informe"
    assert (inst.N, inst.k, inst.B) == (3, 2, 4)
    assert inst.ids() == [1, 2, 3]
    assert inst.conjuntos()[1] == frozenset({"a", "b", "c"})
    assert inst.utilidades()[2].tipo == "raiz"


def test_ordena_los_nodos_por_id():
    datos = {"k": 1, "B": 0, "nodos": [
        {"id": 5, "cubre": [], "utilidad": {"tipo": "log", "a": 1}},
        {"id": 2, "cubre": [], "utilidad": {"tipo": "log", "a": 1}}]}
    assert instancia_desde_diccionario(datos).ids() == [2, 5]


@pytest.mark.parametrize("datos", [
    {"B": 1, "nodos": []},                                                   # falta k
    {"k": "2", "B": 1, "nodos": []},                                         # k no entero
    {"k": 1, "B": 1, "nodos": [{"id": 1, "cubre": []}]},                     # falta utilidad
    {"k": 1, "B": 1, "nodos": [{"id": 1, "cubre": "ab", "utilidad": {"tipo": "log", "a": 1}}]},
    {"k": 1, "B": 1, "nodos": [{"id": 1, "cubre": [], "utilidad": {"tipo": "otra"}}]},
])
def test_formatos_invalidos(datos):
    with pytest.raises(ErrorDeFormato):
        instancia_desde_diccionario(datos)


def caso_con_utilidad(utilidad, cubre=()):
    return {"k": 1, "B": 1, "nodos": [{"id": 1, "cubre": list(cubre), "utilidad": utilidad}]}


@pytest.mark.parametrize("datos", [
    5,                                                                 # raíz que no es objeto
    None,
    [1, 2],
    "k B nodos",
    {"k": 1, "B": 1, "nodos": [5]},                                    # nodo que no es objeto
    {"k": 1, "B": 1, "nodos": [None]},
    {"k": 1, "B": 1, "nodos": ["id cubre utilidad"]},
    caso_con_utilidad(5),                                              # utilidad que no es objeto
    caso_con_utilidad(None),
    caso_con_utilidad("log"),
    caso_con_utilidad({"tipo": "log", "a": 1}, cubre=[["a"]]),         # elementos no hashables
    caso_con_utilidad({"tipo": "log", "a": 1}, cubre=[{"x": 1}]),
    caso_con_utilidad({"tipo": "log"}),                                # falta a
    caso_con_utilidad({"tipo": "tabla"}),                              # falta ganancias
])
def test_formas_que_antes_tumbaban_el_programa(datos):
    # H1: estos casos lanzaban TypeError o AttributeError en vez de ErrorDeFormato
    with pytest.raises(ErrorDeFormato):
        instancia_desde_diccionario(datos)


@pytest.mark.parametrize("tipo", ["log", "raiz"])
@pytest.mark.parametrize("a", [0, 0.0, -1, -0.5, True, False, "3", None, [1], float("nan"),
                               float("inf"), float("-inf"), 10**400])
def test_coeficiente_debe_ser_finito_y_positivo(tipo, a):
    # H9: antes a = Infinity salía en [OK] y a = "3" se convertía sin avisar
    with pytest.raises(ErrorDeFormato):
        instancia_desde_diccionario(caso_con_utilidad({"tipo": tipo, "a": a}))


@pytest.mark.parametrize("texto", ["NaN", "Infinity", "-Infinity", "1e999"])
def test_coeficiente_no_finito_escrito_en_el_json(tmp_path, texto):
    ruta = tmp_path / "caso.json"
    ruta.write_text('{"k":1,"B":1,"nodos":[{"id":1,"cubre":[],"utilidad":{"tipo":"log","a":%s}}]}' % texto,
                    encoding="utf-8")
    with pytest.raises(ErrorDeFormato):
        leer_instancia(ruta)


@pytest.mark.parametrize("a", [1, 0.5, 9.0, 1e-3])
def test_coeficiente_valido_se_acepta(a):
    inst = instancia_desde_diccionario(caso_con_utilidad({"tipo": "raiz", "a": a}))
    assert inst.utilidades()[1].a == a


@pytest.mark.parametrize("ganancias", [5, "abc", {}, {"a": 1}, None, [1, None], [1, "2"], [True],
                                       [float("nan")], [float("inf")], [10**400]])
def test_ganancias_deben_ser_una_lista_de_numeros_finitos(ganancias):
    with pytest.raises(ErrorDeFormato):
        instancia_desde_diccionario(caso_con_utilidad({"tipo": "tabla", "ganancias": ganancias}))


def test_tabla_negativa_no_es_error_de_forma():
    # La forma no juzga la concavidad: eso lo revisa verificacion.py y queda en la traza
    inst = instancia_desde_diccionario(caso_con_utilidad({"tipo": "tabla", "ganancias": [1, 10, -3]}))
    assert inst.utilidades()[1].ganancias == [1, 10, -3]


@pytest.mark.parametrize("contenido", [
    b"{k:",                                       # JSON mal escrito
    b"",                                          # vacío
    b'{"k":1,"B":1,"nodos":[{"id":1,"cubre":["\xf1"],"utilidad":{"tipo":"log","a":1}}]}',  # latin-1
    b"[" * 100000,                                # anidado sin fin
    b'{"k":1' + b"0" * 5000 + b"}",               # entero más largo de lo que Python convierte
])
def test_archivos_que_no_se_pueden_interpretar(tmp_path, contenido):
    ruta = tmp_path / "caso.json"
    ruta.write_bytes(contenido)
    with pytest.raises(ErrorDeFormato):
        leer_instancia(ruta)


def test_lee_utf8_con_bom(tmp_path):
    # H12: el BOM es la marca invisible que agregan algunos editores de Windows
    ruta = tmp_path / "caso.json"
    datos = caso_con_utilidad({"tipo": "log", "a": 1}, cubre=["ñ"])
    ruta.write_bytes(b"\xef\xbb\xbf" + json.dumps(datos, ensure_ascii=False).encode("utf-8"))
    assert leer_instancia(ruta).conjuntos()[1] == frozenset({"ñ"})


@pytest.mark.parametrize("ruta, nombre", [
    ("casos/c.json", "c"),
    ("casos\\c.json", "c"),
    ("c.JSON", "c"),
    ("c.Json", "c"),
    ("sin_extension", "sin_extension"),
    ("otro.txt", "otro.txt"),
])
def test_nombre_del_caso(ruta, nombre):
    assert nombre_del_caso(ruta) == nombre
